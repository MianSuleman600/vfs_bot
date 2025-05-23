# captcha_solver/base.py

from abc import ABC, abstractmethod

class CaptchaSolver(ABC):
    @abstractmethod
    def solve(self, sitekey: str, page_url: str) -> str:
        pass
