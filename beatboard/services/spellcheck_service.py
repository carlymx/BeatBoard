"""SpellCheck service for BeatBoard using Hunspell dictionaries."""

import os
import re
from pathlib import Path
from typing import Optional

try:
    from spylls.hunspell import Dictionary
    SPYLLS_AVAILABLE = True
except ImportError:
    SPYLLS_AVAILABLE = False

from beatboard.core.constants import APP_NAME


LANG_NAMES = {
    "es_ES": "Español",
    "en_US": "English",
    "fr_FR": "Français",
    "de_DE": "Deutsch",
}


class SpellCheckService:
    """Servicio de spellcheck para BeatBoard."""
    
    _instance: Optional["SpellCheckService"] = None
    
    def __new__(cls) -> "SpellCheckService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        
        self._enabled = False
        self._current_lang = "es_ES"
        self._user_words: set[str] = set()
        self._dictionaries: dict[str, Dictionary] = {}
        self._available_languages: list[str] = []
        self._user_dict_path: Optional[Path] = None
        self._user_dict_loaded = False
        
        self._initialized = True
    
    @property
    def is_available(self) -> bool:
        """Retorna si spylls está disponible."""
        return SPYLLS_AVAILABLE
    
    def initialize(self, config_dir: Path) -> None:
        """Inicializa el servicio con el directorio de configuración."""
        self._user_dict_path = config_dir
        self._available_languages = self._load_all_dictionaries()
        self._user_words = self._load_user_dictionary_for_lang(self._current_lang)
    
    def _get_base_path(self) -> Path:
        """Obtiene la ruta base del paquete beatboard."""
        import beatboard
        import sys
        
        # Si estamos en un executable PyInstaller, usar sys._MEIPASS
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        
        return Path(beatboard.__file__).parent
    
    def _get_resources_path(self) -> Path:
        """Obtiene la ruta de diccionarios incluidos."""
        resources = self._get_base_path() / "resources" / "dictionaries"
        
        # Si no existe en la ruta base, intentar en el directorio actual
        if not resources.exists():
            resources = Path("beatboard/resources/dictionaries")
        
        # Si aún no existe, buscar en rutas alternativas
        if not resources.exists():
            # Buscar en el directorio del ejecutable o script
            import sys
            if getattr(sys, 'frozen', False):
                base = Path(sys.executable).parent
            else:
                base = Path(__file__).parent.parent.parent
            resources = base / "resources" / "dictionaries"
        
        return resources
    
    def _get_user_dicts_path(self) -> Path:
        """Obtiene la ruta de diccionarios del usuario."""
        import platform
        
        if platform.system() == "Windows":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif platform.system() == "Darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home() / ".config"
        
        return base / APP_NAME.lower() / "dictionaries"
    
    def _load_all_dictionaries(self) -> list[str]:
        """Carga todos los diccionarios disponibles."""
        loaded = []
        
        resources_path = self._get_resources_path()
        if resources_path.exists():
            for lang_dir in resources_path.iterdir():
                if lang_dir.is_dir():
                    lang_code = lang_dir.name
                    if self._load_dictionary_from_path(lang_code, lang_dir):
                        loaded.append(lang_code)
        
        user_dicts_path = self._get_user_dicts_path()
        if user_dicts_path.exists():
            for lang_dir in user_dicts_path.iterdir():
                if lang_dir.is_dir():
                    lang_code = lang_dir.name
                    if self._load_dictionary_from_path(lang_code, lang_dir):
                        if lang_code not in loaded:
                            loaded.append(lang_code)
        
        if not loaded:
            import sys
            print(
                f"Warning: No dictionaries loaded. "
                f"Searched in: {resources_path} and {user_dicts_path}",
                file=sys.stderr
            )
        
        return loaded
    
    def _load_dictionary_from_path(self, lang_code: str, dict_path: Path) -> bool:
        """Carga un diccionario desde una ruta específica."""
        if not SPYLLS_AVAILABLE:
            return False
        
        aff_file = dict_path / f"{lang_code}.aff"
        dic_file = dict_path / f"{lang_code}.dic"
        
        if not aff_file.exists() or not dic_file.exists():
            return False
        
        try:
            self._dictionaries[lang_code] = Dictionary.from_files(
                str(dict_path / lang_code)
            )
            return True
        except Exception as e:
            import sys
            print(f"Error loading dictionary {lang_code}: {e}", file=sys.stderr)
            return False
    
    def _load_user_dictionary(self) -> None:
        """Carga el diccionario personal del usuario para el idioma actual."""
        if not self._user_dict_path:
            return
        
        user_dict_file = self._user_dict_path.parent / f"user_dictionary_{self._current_lang}.txt"
        
        if not user_dict_file.exists():
            return
        
        try:
            with open(user_dict_file, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self._user_words.add(word.lower())
            self._user_dict_loaded = True
        except Exception:
            pass
    
    def _save_user_dictionary(self) -> None:
        """Guarda el diccionario personal del usuario para el idioma actual."""
        if not self._user_dict_path:
            return
        
        user_dict_file = self._user_dict_path / f"user_dictionary_{self._current_lang}.txt"
        
        try:
            user_dict_file.parent.mkdir(parents=True, exist_ok=True)
            with open(user_dict_file, "w", encoding="utf-8") as f:
                for word in sorted(self._user_words):
                    f.write(word + "\n")
        except Exception as e:
            print(f"Error saving user dictionary: {e}")
    
    def _load_user_dictionary_for_lang(self, lang_code: str) -> set[str]:
        """Carga el diccionario de usuario para un idioma específico."""
        if not self._user_dict_path:
            return set()
        
        user_dict_file = self._user_dict_path / f"user_dictionary_{lang_code}.txt"
        
        if not user_dict_file.exists():
            return set()
        
        words = set()
        try:
            with open(user_dict_file, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if word:
                        words.add(word.lower())
        except Exception:
            pass
        
        return words
    
    def get_available_languages(self) -> list[tuple[str, str]]:
        """Retorna lista de diccionarios disponibles como (código, nombre)."""
        result = []
        for lang_code in sorted(self._available_languages):
            name = LANG_NAMES.get(lang_code, lang_code)
            result.append((lang_code, name))
        return result
    
    def set_language(self, lang_code: str) -> bool:
        """Establece el idioma activo."""
        if lang_code in self._dictionaries:
            self._current_lang = lang_code
            self._user_words = self._load_user_dictionary_for_lang(lang_code)
            return True
        return False
    
    def get_current_language(self) -> str:
        """Retorna el idioma activo."""
        return self._current_lang
    
    def is_enabled(self) -> bool:
        """Retorna si el spellcheck está activo."""
        return self._enabled
    
    def set_enabled(self, enabled: bool) -> None:
        """Activa/desactiva el spellcheck."""
        self._enabled = enabled
    
    def check_word(self, word: str) -> bool:
        """Verifica si una palabra está bien escrita."""
        if not self._enabled or not SPYLLS_AVAILABLE:
            return True
        
        word_lower = word.lower()
        
        if word_lower in self._user_words:
            return True
        
        dictionary = self._dictionaries.get(self._current_lang)
        if dictionary is None:
            return True
        
        return dictionary.lookup(word)
    
    def get_suggestions(self, word: str) -> list[str]:
        """Retorna sugerencias para una palabra mal escrita."""
        if not self._enabled or not SPYLLS_AVAILABLE:
            return []
        
        suggestions = []
        
        dictionary = self._dictionaries.get(self._current_lang)
        if dictionary is not None:
            try:
                suggestions = list(dictionary.suggest(word))
            except Exception:
                pass
        
        for user_word in self._user_words:
            if self._is_similar(word.lower(), user_word):
                if user_word not in suggestions:
                    suggestions.append(user_word)
        
        return suggestions[:10]
    
    def _is_similar(self, word1: str, word2: str, max_distance: int = 2) -> bool:
        """Compara dos palabras y retorna True si son similares (distancia de Levenshtein)."""
        if abs(len(word1) - len(word2)) > max_distance:
            return False
        
        distance = 0
        i, j = 0, 0
        
        while i < len(word1) and j < len(word2):
            if word1[i] != word2[j]:
                distance += 1
                if distance > max_distance:
                    return False
                if len(word1) > len(word2):
                    i += 1
                elif len(word1) < len(word2):
                    j += 1
                else:
                    i += 1
                    j += 1
            else:
                i += 1
                j += 1
        
        distance += len(word1) - i + len(word2) - j
        return distance <= max_distance
    
    def add_to_user_dict(self, word: str) -> None:
        """Añade palabra al diccionario del usuario."""
        word_lower = word.lower()
        self._user_words.add(word_lower)
        self._save_user_dictionary()
    
    def ignore_word(self, word: str) -> None:
        """Añade palabra a la lista de ignorados temporalmente."""
        pass
    
    def get_word_at_cursor(self, text: str, cursor_pos: int) -> tuple[str, int, int]:
        """Obtiene la palabra en la posición del cursor.
        
        Returns:
            (word, start_pos, end_pos)
        """
        if cursor_pos > len(text):
            return "", -1, -1
        
        pattern = r'\b\w+\b'
        for match in re.finditer(pattern, text):
            if match.start() <= cursor_pos <= match.end():
                return match.group(), match.start(), match.end()
        
        return "", -1, -1
    
    @classmethod
    def instance(cls) -> "SpellCheckService":
        """Retorna la instancia singleton del servicio."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


spell_check_service = SpellCheckService.instance()
