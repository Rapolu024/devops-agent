"""
Repository Analyzer - Downloads and analyzes repository structure
"""

import os
import git
import json
import asyncio
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

@dataclass
class FileInfo:
    path: str
    size: int
    extension: str
    content: Optional[str] = None

@dataclass
class RepositoryData:
    url: str
    name: str
    structure: Dict[str, Any]
    files: List[FileInfo]
    total_files: int
    total_size: int
    languages: Dict[str, int]

class RepositoryAnalyzer:
    """Analyzes repository structure and content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.temp_dir = None
        
    async def analyze(self, repo_url: str) -> RepositoryData:
        """Analyze a repository from URL"""
        self.logger.info(f"Analyzing repository: {repo_url}")
        
        try:
            # Clone repository
            repo_path = await self._clone_repository(repo_url)
            
            # Analyze structure
            structure = await self._analyze_structure(repo_path)
            
            # Get file information
            files = await self._get_file_info(repo_path)
            
            # Analyze languages
            languages = await self._analyze_languages(files)
            
            # Create repository data
            repo_data = RepositoryData(
                url=repo_url,
                name=self._extract_repo_name(repo_url),
                structure=structure,
                files=files,
                total_files=len(files),
                total_size=sum(f.size for f in files),
                languages=languages
            )
            
            # Cleanup
            await self._cleanup()
            
            return repo_data
            
        except Exception as e:
            await self._cleanup()
            self.logger.error(f"Failed to analyze repository: {str(e)}")
            raise
    
    async def _clone_repository(self, repo_url: str) -> str:
        """Clone repository to temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        repo_path = os.path.join(self.temp_dir, "repo")
        
        try:
            # Clone repository
            git.Repo.clone_from(repo_url, repo_path)
            self.logger.info(f"Repository cloned to: {repo_path}")
            return repo_path
        except Exception as e:
            self.logger.error(f"Failed to clone repository: {str(e)}")
            raise
    
    async def _analyze_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze directory structure"""
        structure = {}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == '.':
                rel_path = ''
            
            current_level = structure
            if rel_path:
                for part in rel_path.split(os.sep):
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]
            
            # Add files to current level
            for file in files:
                if not file.startswith('.'):
                    current_level[file] = "file"
        
        return structure
    
    async def _get_file_info(self, repo_path: str) -> List[FileInfo]:
        """Get detailed information about all files"""
        files = []
        
        for root, dirs, filenames in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, repo_path)
                
                try:
                    size = os.path.getsize(file_path)
                    extension = Path(filename).suffix.lower()
                    
                    # Read content for text files (up to 1MB)
                    content = None
                    if size < 1024 * 1024 and self._is_text_file(extension):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        except (UnicodeDecodeError, IOError):
                            pass
                    
                    files.append(FileInfo(
                        path=rel_path,
                        size=size,
                        extension=extension,
                        content=content
                    ))
                    
                except OSError:
                    continue
        
        return files
    
    async def _analyze_languages(self, files: List[FileInfo]) -> Dict[str, int]:
        """Analyze programming languages used"""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.sh': 'Shell',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS'
        }
        
        languages = {}
        for file in files:
            if file.extension in language_map:
                lang = language_map[file.extension]
                languages[lang] = languages.get(lang, 0) + file.size
        
        return languages
    
    def _is_text_file(self, extension: str) -> bool:
        """Check if file is a text file"""
        text_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs',
            '.php', '.rb', '.swift', '.kt', '.scala', '.sh', '.yml',
            '.yaml', '.json', '.xml', '.html', '.css', '.scss', '.less',
            '.md', '.txt', '.cfg', '.conf', '.ini', '.env', '.gitignore',
            '.dockerfile', '.sql', '.r', '.m', '.pl', '.lua'
        }
        return extension in text_extensions
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL"""
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        return repo_url.split('/')[-1]
    
    async def _cleanup(self):
        """Cleanup temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info("Cleaned up temporary files")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup: {str(e)}")
