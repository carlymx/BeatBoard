"""Project packager - Handles ZIP-based project files (.bbp)."""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path
from typing import Literal

from beatboard.core.project import Project


class ProjectPackager:
    """Handles packing and unpacking BeatBoard projects as ZIP archives."""

    PROJECT_JSON = "project.json"
    BEATS_DIR = "beats"
    THUMBNAILS_DIR = "thumbnails"

    @staticmethod
    def detect_format(file_path: Path) -> Literal["json", "zip"]:
        """Detect if a file is JSON or ZIP format.
        
        Args:
            file_path: Path to the project file.
            
        Returns:
            "json" for old-style JSON files, "zip" for new ZIP format.
        """
        try:
            with open(file_path, "rb") as f:
                header = f.read(4)
                if header == b"PK\x03\x04":
                    return "zip"
        except Exception:
            pass
        return "json"

    @staticmethod
    def pack(project: Project, output_path: Path) -> None:
        """Save a project as a ZIP archive.
        
        Args:
            project: The Project to save.
            output_path: Path where the .bbp file will be saved.
        """
        import shutil
        import sys
        
        project.update_modified()
        
        images_dir = output_path.parent / f".{output_path.stem}_data"
        images_dir.mkdir(exist_ok=True)
        
        # NO modificar project.project_path durante el guardado
        # project.project_path = images_dir
        
        beats_dir = images_dir / "beats"
        beats_dir.mkdir(exist_ok=True)
        media_dir = images_dir / "media"
        media_dir.mkdir(exist_ok=True)
        

        
        # Mapeo de rutas originales a rutas relativas dentro del ZIP
        # Para evitar duplicados, usamos hash de la ruta original
        imported_images = {}
        
        # Procesar imágenes incrustadas en beats
        for beat in project.beats:
            embedded_images = getattr(beat, 'embedded_images', [])
            if embedded_images:
                beat_images_dir = beats_dir / beat.id
                beat_images_dir.mkdir(exist_ok=True)
                
                for img_info in embedded_images:
                    if isinstance(img_info, dict):
                        src_path = img_info.get('original_path')
                        filename = img_info.get('filename')
                        relative_path = img_info.get('relative_path')
                    else:
                        src_path = img_info
                        filename = Path(img_info).name
                        relative_path = img_info
                    
                    if not src_path or not Path(src_path).exists():
                        continue
                    
                    # Asegurar que filename y relative_path estén definidos
                    if not filename:
                        filename = Path(src_path).name
                    if not relative_path:
                        relative_path = f"beats/{beat.id}/{filename}"
                    
                    dst_path = beat_images_dir / filename
                    shutil.copy2(src_path, dst_path)
                    # Registrar en mapa para posible uso en canvas_images
                    imported_images[src_path] = relative_path
        
        # Procesar imágenes del lienzo (canvas_images)
        canvas_images_modified = []
        for img_data in project.canvas_images:
            src_path = img_data.get("image_path")
            if not src_path:
                continue
            
            # Resolver ruta absoluta
            src_path_obj = Path(src_path)
            if not src_path_obj.is_absolute() and project.project_path:
                # Intentar encontrar en project_path
                possible_paths = [
                    project.project_path / src_path,
                    project.project_path / "media" / src_path_obj.name,
                ]
                # Buscar recursivamente en beats
                beats_glob = list(project.project_path.glob(f"beats/**/{src_path_obj.name}"))
                if beats_glob:
                    possible_paths.extend(beats_glob)
                found = False
                for path in possible_paths:
                    if path.exists():
                        src_path_obj = path
                        found = True
                        break
                # Si no se encuentra, mantener src_path_obj como la ruta original (relativa)
            
            src_abs_path = src_path_obj if src_path_obj.is_absolute() else None
            if src_abs_path and src_abs_path.exists():
                src_key = str(src_abs_path)
            else:
                src_key = src_path  # mantener original
            
            # Verificar si ya está en imported_images (por beats o canvas anterior)
            if src_key in imported_images:
                # Reutilizar ruta relativa existente
                relative_path = imported_images[src_key]
            else:
                # Determinar si el archivo ya está dentro del directorio de medios del proyecto
                project_base = project.project_path if project.project_path else images_dir
                if src_abs_path and src_abs_path.exists():
                    # Verificar si está dentro del proyecto base
                    try:
                        if src_abs_path.is_relative_to(project_base):
                            # Calcular ruta relativa respecto a project_base
                            rel_to_base = src_abs_path.relative_to(project_base)
                            # Si ya está en media/ o beats/, reutilizar
                            if str(rel_to_base).startswith(('media/', 'beats/')):
                                relative_path = str(rel_to_base)
                                imported_images[src_key] = relative_path
                            else:
                                # Está en proyecto pero no en media/beats, copiar a media/
                                import uuid
                                ext = src_abs_path.suffix.lower()
                                if not ext:
                                    ext = ".png"
                                new_filename = f"image_{uuid.uuid4().hex[:8]}{ext}"
                                relative_path = f"media/{new_filename}"
                                dst_path = media_dir / new_filename
                                shutil.copy2(src_abs_path, dst_path)
                                imported_images[src_key] = relative_path
                        else:
                            # Fuera del proyecto, copiar a media/ con nombre único
                            import uuid
                            ext = src_abs_path.suffix.lower()
                            if not ext:
                                ext = ".png"
                            new_filename = f"image_{uuid.uuid4().hex[:8]}{ext}"
                            relative_path = f"media/{new_filename}"
                            dst_path = media_dir / new_filename
                            shutil.copy2(src_abs_path, dst_path)
                            imported_images[src_key] = relative_path
                    except ValueError:
                        # No es relativo a project_base
                        import uuid
                        ext = src_abs_path.suffix.lower()
                        if not ext:
                            ext = ".png"
                        new_filename = f"image_{uuid.uuid4().hex[:8]}{ext}"
                        relative_path = f"media/{new_filename}"
                        dst_path = media_dir / new_filename
                        shutil.copy2(src_abs_path, dst_path)
                        imported_images[src_key] = relative_path
                else:
                    # src_path no existe o no es absoluta, mantener ruta original (relativa)
                    relative_path = src_path
                    imported_images[src_key] = relative_path
            
            # Actualizar datos de imagen con ruta relativa
            img_data_copy = img_data.copy()
            img_data_copy["image_path"] = relative_path
            canvas_images_modified.append(img_data_copy)
        
        # Crear datos del proyecto con imágenes actualizadas
        
        project_dict = project.to_dict()
        if canvas_images_modified:
            project_dict["canvas_images"] = canvas_images_modified
        else:
            # Asegurar que canvas_images esté vacío en el JSON
            project_dict["canvas_images"] = []
        
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            project_data = json.dumps(
                project_dict, 
                indent=2, 
                ensure_ascii=False
            )
            zf.writestr(ProjectPackager.PROJECT_JSON, project_data)
            
            # Agregar archivos de beats
            for beat in project.beats:
                embedded_images = getattr(beat, 'embedded_images', [])
                if embedded_images:
                    for img_info in embedded_images:
                        if isinstance(img_info, dict):
                            filename = img_info.get('filename')
                            relative_path = img_info.get('relative_path')
                            # Si filename es None, intentar obtener de original_path o relative_path
                            if not filename:
                                if img_info.get('original_path'):
                                    filename = Path(img_info['original_path']).name
                                elif relative_path:
                                    filename = Path(relative_path).name
                        else:
                            filename = Path(img_info).name
                            relative_path = img_info
                        
                        if not filename or not relative_path:
                            continue
                        
                        src_in_data_dir = beats_dir / beat.id / str(filename)
                        if src_in_data_dir.exists():
                            zf.write(src_in_data_dir, relative_path)
            
            # Agregar archivos de media
            for src_path, relative_path in imported_images.items():
                if relative_path.startswith("media/"):
                    src_in_data_dir = media_dir / Path(relative_path).name
                    if src_in_data_dir.exists():
                        zf.write(src_in_data_dir, relative_path)

    @staticmethod
    def _collect_embedded_images(project: Project) -> list:
        """Collect all embedded image paths from beats."""
        paths = []
        for beat in project.beats:
            embedded_images = getattr(beat, 'embedded_images', [])
            for img_info in embedded_images:
                if isinstance(img_info, dict):
                    relative_path = img_info.get('relative_path')
                else:
                    relative_path = img_info
                if relative_path and relative_path not in paths:
                    paths.append(img_info)
        return paths

    @staticmethod
    def unpack(zip_path: Path) -> Project:
        """Load a project from a ZIP archive.
        
        Args:
            zip_path: Path to the .bbp ZIP file.
            
        Returns:
            The loaded Project instance.
            
        Raises:
            ValueError: If the ZIP file doesn't contain a valid project.
        """
        import tempfile
        
        temp_dir = None
        try:
            temp_dir = Path(tempfile.mkdtemp(prefix="beatboard_"))
            
            with zipfile.ZipFile(zip_path, "r") as zf:
                if ProjectPackager.PROJECT_JSON not in zf.namelist():
                    raise ValueError(f"Invalid project file: {ProjectPackager.PROJECT_JSON} not found")
                
                with zf.open(ProjectPackager.PROJECT_JSON) as f:
                    data = json.load(f)
                    project = Project.from_dict(data)
                    canvas_images = data.get("canvas_images", [])
                
                extract_dir = temp_dir
                for name in zf.namelist():
                    if name != ProjectPackager.PROJECT_JSON and not name.startswith('/'):
                        zf.extract(name, extract_dir)
                
                project.project_path = zip_path.parent / f".{zip_path.stem}_data"
                project.project_path.mkdir(exist_ok=True)
                
                for name in zf.namelist():
                    if name != ProjectPackager.PROJECT_JSON and not name.startswith('/'):
                        src = extract_dir / name
                        if src.exists():
                            dst = project.project_path / name
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(src), str(dst))
            
            return project
        finally:
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    def load_project(file_path: Path) -> Project:
        """Load a project, detecting format automatically.
        
        Supports both old JSON format and new ZIP format.
        
        Args:
            file_path: Path to the project file (.bbp).
            
        Returns:
            The loaded Project instance.
        """
        format_type = ProjectPackager.detect_format(file_path)
        
        if format_type == "zip":
            return ProjectPackager.unpack(file_path)
        else:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            return Project.from_dict(data)

    @staticmethod
    def save_project(project: Project, file_path: Path) -> None:
        """Save a project, always using ZIP format.
        
        Args:
            project: The Project to save.
            file_path: Path where the .bbp file will be saved.
        """
        ProjectPackager.pack(project, file_path)
