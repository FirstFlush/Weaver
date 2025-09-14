import ua_generator


class Headers:
    
    def _ua(self) -> str:
        return ua_generator.generate().text