"""OCR 识别引擎
支持 PaddleOCR 和 Tesseract 双引擎识别，提供图像预处理、结果融合、缓存和重试机制。
"""

import time
from pathlib import Path
from typing import Optional, List, Tuple
import numpy as np
import cv2
from PIL import Image

from utils.exceptions import OCRException, handle_exceptions
from utils.cache_manager import CacheManager
from utils.log_manager import get_logger


class OCREngine:
    """OCR 识别引擎
    支持 PaddleOCR 和 Tesseract 双引擎识别，提供图像预处理、结果融合、缓存和重试机制。
    """
    
    def __init__(self, use_paddle: bool = True, use_tesseract: bool = True,
                 languages: List[str] = None, cache_manager: CacheManager = None):
        """初始化 OCR 引擎
        
        Args:
            use_paddle: 是否使用 PaddleOCR
            use_tesseract: 是否使用 Tesseract
            languages: OCR 语言列表，默认 ["ch_sim", "en"]
            cache_manager: 缓存管理器实例
            
        Raises:
            OCRException: 初始化失败
        """
        self.use_paddle = use_paddle
        self.use_tesseract = use_tesseract
        self.languages = languages or ["ch_sim", "en"]
        self.cache_manager = cache_manager or CacheManager()
        self.logger = get_logger()
        
        # 验证至少启用一个引擎
        if not use_paddle and not use_tesseract:
            raise OCRException("至少需要启用一个 OCR 引擎")
        
        # 初始化 OCR 引擎
        self.paddle_ocr = None
        self.tesseract_available = False
        
        self._init_paddle_ocr()
        self._init_tesseract()
        
        self.logger.info(
            "OCR 引擎初始化完成",
            paddle_enabled=self.use_paddle and self.paddle_ocr is not None,
            tesseract_enabled=self.use_tesseract and self.tesseract_available
        )
    
    def _init_paddle_ocr(self):
        """初始化 PaddleOCR"""
        if not self.use_paddle:
            return
        
        try:
            from paddleocr import PaddleOCR
            
            # 初始化 PaddleOCR
            # lang='ch' 支持中文
            # 注意：不同版本的 PaddleOCR 参数可能不同，使用最基本的参数
            self.paddle_ocr = PaddleOCR(lang='ch')
            self.logger.info("PaddleOCR 初始化成功")
        except ImportError:
            self.logger.warning("PaddleOCR 未安装，将禁用 PaddleOCR 引擎")
            self.paddle_ocr = None
        except Exception as e:
            self.logger.error(f"PaddleOCR 初始化失败: {e}")
            self.paddle_ocr = None
    
    def _init_tesseract(self):
        """初始化 Tesseract"""
        if not self.use_tesseract:
            return
        
        try:
            import pytesseract
            
            # 测试 Tesseract 是否可用
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
            self.logger.info("Tesseract 初始化成功")
        except Exception as e:
            self.logger.warning(f"Tesseract 不可用: {e}")
            self.tesseract_available = False
    
    @handle_exceptions(reraise=True)
    def extract_text(self, file_path: str, max_retries: int = 3) -> str:
        """从文件中提取文本"""
        start_time = time.time()
        file_path = str(Path(file_path).resolve())
        
        # 验证文件存在
        if not Path(file_path).exists():
            raise OCRException(
                f"文件不存在: {file_path}",
                file_path=file_path
            )
        
        # 验证文件格式
        supported_formats = ['.png', '.jpg', '.jpeg', '.pdf']
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in supported_formats:
            raise OCRException(
                f"不支持的文件格式: {file_ext}，支持的格式: {', '.join(supported_formats)}",
                file_path=file_path
            )
        
        self.logger.log_operation(
            "OCR_START",
            file_path=file_path,
            file_size=Path(file_path).stat().st_size
        )
        
        # 检查缓存
        cached_text = self.cache_manager.get_ocr_cache(file_path)
        if cached_text:
            self.logger.info("使用 OCR 缓存", file_path=file_path)
            return cached_text
        
        # 处理 PDF 文件
        if file_ext == '.pdf':
            text = self._extract_text_from_pdf(file_path, max_retries)
        else:
            text = self._extract_text_from_image(file_path, max_retries)
        
        # 缓存结果
        if text:
            self.cache_manager.set_ocr_cache(file_path, text)
        
        duration = time.time() - start_time
        self.logger.log_performance(
            "OCR_COMPLETE",
            duration=duration,
            file_path=file_path,
            text_length=len(text)
        )
        
        return text
    
    def _extract_text_from_image(self, file_path: str, max_retries: int) -> str:
        """从图像文件中提取文本"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # 读取图像
                image = cv2.imread(file_path)
                if image is None:
                    raise OCRException(
                        f"无法读取图像文件: {file_path}",
                        file_path=file_path
                    )
                
                # 预处理图像
                processed_image = self.preprocess_image(image)
                
                # 双引擎识别
                paddle_result = []
                tesseract_result = []
                
                if self.paddle_ocr:
                    try:
                        paddle_result = self._paddle_ocr(processed_image)
                    except Exception as e:
                        self.logger.warning(f"PaddleOCR 识别失败: {e}")
                
                if self.tesseract_available:
                    try:
                        tesseract_result = self._tesseract_ocr(processed_image)
                    except Exception as e:
                        self.logger.warning(f"Tesseract 识别失败: {e}")
                
                # 融合结果
                text = self._merge_results(paddle_result, tesseract_result)
                
                if not text:
                    raise OCRException(
                        "OCR 识别结果为空",
                        file_path=file_path
                    )
                
                return text
                
            except OCRException as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避: 1s, 2s, 4s
                    self.logger.warning(
                        f"OCR 识别失败，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    # 最后一次尝试失败，尝试降级为单引擎模式
                    self.logger.warning("尝试降级为单引擎模式")
                    return self._fallback_single_engine(file_path)
            except Exception as e:
                last_exception = OCRException(
                    f"OCR 识别异常: {str(e)}",
                    file_path=file_path
                )
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(
                        f"OCR 识别异常，{wait_time}秒后重试: {e}"
                    )
                    time.sleep(wait_time)
        
        # 所有重试都失败
        raise last_exception or OCRException(
            "OCR 识别失败",
            file_path=file_path
        )
    
    def _extract_text_from_pdf(self, file_path: str, max_retries: int) -> str:
        """从 PDF 文件中提取文本"""
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise OCRException(
                "pdf2image 未安装，无法处理 PDF 文件。请安装: pip install pdf2image",
                file_path=file_path
            )
        
        try:
            # 将 PDF 转换为图像列表
            images = convert_from_path(file_path, dpi=300)
            
            if not images:
                raise OCRException(
                    "PDF 文件为空或无法转换",
                    file_path=file_path
                )
            
            # 对每一页进行 OCR 识别
            all_text = []
            for page_num, pil_image in enumerate(images, 1):
                self.logger.debug(f"处理 PDF 第 {page_num}/{len(images)} 页")
                
                # 将 PIL Image 转换为 numpy array
                image = np.array(pil_image)
                # 转换 RGB 到 BGR (OpenCV 格式)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # 预处理图像
                processed_image = self.preprocess_image(image)
                
                # 双引擎识别
                paddle_result = []
                tesseract_result = []
                
                if self.paddle_ocr:
                    try:
                        paddle_result = self._paddle_ocr(processed_image)
                    except Exception as e:
                        self.logger.warning(f"PaddleOCR 识别第 {page_num} 页失败: {e}")
                
                if self.tesseract_available:
                    try:
                        tesseract_result = self._tesseract_ocr(processed_image)
                    except Exception as e:
                        self.logger.warning(f"Tesseract 识别第 {page_num} 页失败: {e}")
                
                # 融合结果
                page_text = self._merge_results(paddle_result, tesseract_result)
                if page_text:
                    all_text.append(f"--- 第 {page_num} 页 ---\n{page_text}")
            
            if not all_text:
                raise OCRException(
                    "PDF 所有页面识别结果为空",
                    file_path=file_path
                )
            
            return "\n\n".join(all_text)
            
        except OCRException:
            raise
        except Exception as e:
            raise OCRException(
                f"PDF 处理失败: {str(e)}",
                file_path=file_path
            )
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """图像预处理"""
        # 1. 灰度化转换
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 2. 高斯去噪
        denoised = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 3. 自适应对比度增强 (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 4. 角度校正
        corrected = self._correct_skew(enhanced)
        
        return corrected
    
    def _correct_skew(self, image: np.ndarray) -> np.ndarray:
        """角度校正"""
        try:
            # 边缘检测
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            
            # Hough 变换检测直线
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
            
            if lines is None or len(lines) == 0:
                return image
            
            # 计算平均角度
            angles = []
            for line in lines[:10]:  # 只使用前 10 条线
                rho, theta = line[0]
                angle = np.degrees(theta) - 90
                if -45 < angle < 45:  # 只考虑合理的角度
                    angles.append(angle)
            
            if not angles:
                return image
            
            avg_angle = np.median(angles)
            
            # 如果角度很小，不需要校正
            if abs(avg_angle) < 0.5:
                return image
            
            # 旋转图像
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            
            self.logger.debug(f"图像角度校正: {avg_angle:.2f}°")
            return rotated
            
        except Exception as e:
            self.logger.warning(f"角度校正失败: {e}")
            return image
    
    def _paddle_ocr(self, image: np.ndarray) -> List[str]:
        """PaddleOCR 识别"""
        if not self.paddle_ocr:
            return []
        
        try:
            result = self.paddle_ocr.ocr(image, cls=True)
            
            if not result or not result[0]:
                return []
            
            # 提取文本
            text_lines = []
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]  # line[1] 是 (text, confidence)
                    if text and isinstance(text, str):
                        text_lines.append(text.strip())
            
            return text_lines
            
        except Exception as e:
            self.logger.warning(f"PaddleOCR 识别异常: {e}")
            return []
    
    def _tesseract_ocr(self, image: np.ndarray) -> List[str]:
        """Tesseract 识别"""
        if not self.tesseract_available:
            return []
        
        try:
            import pytesseract
            
            # 配置 Tesseract
            # lang='chi_sim+eng' 支持中英文
            config = '--psm 6'  # PSM 6: 假设单个文本块
            
            text = pytesseract.image_to_string(
                image,
                lang='chi_sim+eng',
                config=config
            )
            
            if not text:
                return []
            
            # 分割为行并清理
            text_lines = [
                line.strip()
                for line in text.split('\n')
                if line.strip()
            ]
            
            return text_lines
            
        except Exception as e:
            self.logger.warning(f"Tesseract 识别异常: {e}")
            return []
    
    def _merge_results(self, paddle_result: List[str],
                      tesseract_result: List[str]) -> str:
        """合并多引擎结果:优先使用 PaddleOCR 结果，Tesseract 作为补充"""
        # 如果只有一个引擎有结果，直接使用
        if paddle_result and not tesseract_result:
            return '\n'.join(paddle_result)
        
        if tesseract_result and not paddle_result:
            return '\n'.join(tesseract_result)
        
        if not paddle_result and not tesseract_result:
            return ""
        
        # 两个引擎都有结果，优先使用 PaddleOCR
        # 但如果 Tesseract 结果明显更长，可能识别更完整
        paddle_text = '\n'.join(paddle_result)
        tesseract_text = '\n'.join(tesseract_result)
        
        # 如果 Tesseract 结果长度超过 PaddleOCR 的 1.5 倍，使用 Tesseract
        if len(tesseract_text) > len(paddle_text) * 1.5:
            self.logger.debug("使用 Tesseract 结果（更完整）")
            return tesseract_text
        
        # 否则使用 PaddleOCR 结果
        self.logger.debug("使用 PaddleOCR 结果")
        return paddle_text
    
    def _fallback_single_engine(self, file_path: str) -> str:
        """降级为单引擎模式:当双引擎都失败时，尝试单独使用每个引擎"""
        self.logger.info("尝试单引擎降级模式")
        
        try:
            image = cv2.imread(file_path)
            if image is None:
                raise OCRException(
                    f"无法读取图像文件: {file_path}",
                    file_path=file_path
                )
            
            # 简单预处理（不进行角度校正）
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 尝试 PaddleOCR
            if self.paddle_ocr:
                try:
                    paddle_result = self._paddle_ocr(gray)
                    if paddle_result:
                        text = '\n'.join(paddle_result)
                        self.logger.info("单引擎模式 (PaddleOCR) 成功")
                        return text
                except Exception as e:
                    self.logger.warning(f"单引擎 PaddleOCR 失败: {e}")
            
            # 尝试 Tesseract
            if self.tesseract_available:
                try:
                    tesseract_result = self._tesseract_ocr(gray)
                    if tesseract_result:
                        text = '\n'.join(tesseract_result)
                        self.logger.info("单引擎模式 (Tesseract) 成功")
                        return text
                except Exception as e:
                    self.logger.warning(f"单引擎 Tesseract 失败: {e}")
            
            raise OCRException(
                "所有 OCR 引擎（包括降级模式）都失败",
                file_path=file_path
            )
            
        except OCRException:
            raise
        except Exception as e:
            raise OCRException(
                f"降级模式失败: {str(e)}",
                file_path=file_path
            )
