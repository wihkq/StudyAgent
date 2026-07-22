"""OCR Provider — 图片文字识别接口

可替换实现：MockOCR / PaddleOCR
"""
import logging

logger = logging.getLogger(__name__)


class OCRProvider:
    """OCR 抽象基类"""

    async def recognize(self, image_data: bytes) -> str:
        """识别图片中的文字

        Args:
            image_data: 图片二进制数据

        Returns:
            识别出的文字内容，无文字时返回空字符串
        """
        raise NotImplementedError


class MockOCR(OCRProvider):
    """Mock OCR — 返回固定演示文字，用于无 OCR 引擎时的流程验证"""

    async def recognize(self, image_data: bytes) -> str:
        """Mock 识别：对非空图片返回固定文字"""
        if not image_data:
            return ""
        # 返回演示文字，模拟 OCR 识别结果
        return "（图片文字识别结果）"


def get_ocr() -> OCRProvider:
    """工厂函数：根据全局配置返回 OCR 实例"""
    from config.settings import Settings

    ocr_mode = Settings().ocr_mode
    if ocr_mode == "mock":
        return MockOCR()
    elif ocr_mode == "paddle":
        logger.warning("OCR_MODE=paddle 配置已设置，但 PaddleOCR 尚未集成，回退 MockOCR")
        return MockOCR()
    else:
        logger.warning("未知 OCR_MODE=%s，回退 MockOCR", ocr_mode)
        return MockOCR()


__all__ = ["OCRProvider", "MockOCR", "get_ocr"]
