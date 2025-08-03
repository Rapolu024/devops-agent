"""
Code Understanding Engine - Analyzes code patterns and extracts insights
"""

import re
import ast
import json
import logging
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass
from pathlib import Path

from repository_analyzer import RepositoryData, FileInfo

@dataclass
class CodeInsights:
    project_type: str
    languages: List[str]
    frameworks: List[str]
    dependencies: Dict[str, Any]
    deployment_requirements: Dict[str, Any]
    security_requirements: List[str]
    performance_requirements: Dict[str, Any]
    database_usage: List[str]
    api_endpoints: List[Dict[str, Any]]
    environment_variables: List[str]
    build_tools: List[str]

class CodeUnderstandingEngine:
    """Analyzes code to understand project structure and requirements"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.framework_patterns = self._load_framework_patterns()
        self.dependency_patterns = self._load_dependency_patterns()
    
    async def analyze_codebase(self, repo_data: RepositoryData) -> CodeInsights:
        """Analyze codebase and extract insights"""
        self.logger.info("Starting code analysis")
        
        # Determine project type
        project_type = await self._determine_project_type(repo_data)
        
        # Extract languages
        languages = list(repo_data.languages.keys())
        
        # Detect frameworks
        frameworks = await self._detect_frameworks(repo_data)
        
        # Analyze dependencies
        dependencies = await self._analyze_dependencies(repo_data)
        
        # Determine deployment requirements
        deployment_reqs = await self._analyze_deployment_requirements(repo_data)
        
        # Analyze security requirements
        security_reqs = await self._analyze_security_requirements(repo_data)
        
        # Analyze performance requirements
        performance_reqs = await self._analyze_performance_requirements(repo_data)
        
        # Detect database usage
        databases = await self._detect_database_usage(repo_data)
        
        # Extract API endpoints
        api_endpoints = await self._extract_api_endpoints(repo_data)
        
        # Find environment variables
        env_vars = await self._find_environment_variables(repo_data)
        
        # Detect build tools
        build_tools = await self._detect_build_tools(repo_data)
        
        return CodeInsights(
            project_type=project_type,
            languages=languages,
            frameworks=frameworks,
            dependencies=dependencies,
            deployment_requirements=deployment_reqs,
            security_requirements=security_reqs,
            performance_requirements=performance_reqs,
            database_usage=databases,
            api_endpoints=api_endpoints,
            environment_variables=env_vars,
            build_tools=build_tools
        )
    
    async def _determine_project_type(self, repo_data: RepositoryData) -> str:
        """Determine the type of project"""
        # Check for specific files that indicate project type
        files = {f.path.lower() for f in repo_data.files}
        
        if 'package.json' in files:
            # Analyze package.json to determine if it's frontend or backend
            package_json = next((f for f in repo_data.files if f.path.lower() == 'package.json'), None)
            if package_json and package_json.content:
                try:
                    pkg_data = json.loads(package_json.content)
                    deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
                    
                    frontend_indicators = ['react', 'vue', 'angular', 'svelte', 'next', 'nuxt']
                    backend_indicators = ['express', 'koa', 'fastify', 'nest']
                    
                    if any(indicator in deps for indicator in frontend_indicators):
                        return 'frontend'
                    elif any(indicator in deps for indicator in backend_indicators):
                        return 'backend'
                    else:
                        return 'nodejs'
                except json.JSONDecodeError:
                    pass
        
        if 'requirements.txt' in files or 'pyproject.toml' in files or 'setup.py' in files:
            # Check if it's a web framework
            for file in repo_data.files:
                if file.content and any(framework in file.content.lower() 
                                      for framework in ['django', 'flask', 'fastapi']):
                    return 'web_backend'
            return 'python'
        
        if 'pom.xml' in files or 'build.gradle' in files:
            return 'java'
        
        if 'go.mod' in files:
            return 'go'
        
        if 'cargo.toml' in files:
            return 'rust'
        
        if 'composer.json' in files:
            return 'php'
        
        if 'dockerfile' in files or 'docker-compose.yml' in files:
            return 'containerized'
        
        # Default classification based on primary language
        if repo_data.languages:
            primary_lang = max(repo_data.languages.items(), key=lambda x: x[1])[0].lower()
            return primary_lang
        
        return 'unknown'
    
    async def _detect_frameworks(self, repo_data: RepositoryData) -> List[str]:
        """Detect frameworks used in the project"""
        frameworks = set()
        
        for file in repo_data.files:
            if file.content:
                content_lower = file.content.lower()
                
                # Check for framework patterns
                for pattern, framework in self.framework_patterns.items():
                    if re.search(pattern, content_lower, re.IGNORECASE):
                        frameworks.add(framework)
        
        # Check package files
        package_files = ['package.json', 'requirements.txt', 'pom.xml', 'go.mod', 'cargo.toml']
        for file in repo_data.files:
            if file.path.lower() in package_files and file.content:
                frameworks.update(self._extract_frameworks_from_package(file))
        
        return list(frameworks)
    
    async def _analyze_dependencies(self, repo_data: RepositoryData) -> Dict[str, Any]:
        """Analyze project dependencies"""
        dependencies = {
            'direct': {},
            'dev': {},
            'runtime': []
        }
        
        for file in repo_data.files:
            if file.path.lower() == 'package.json' and file.content:
                try:
                    pkg_data = json.loads(file.content)
                    dependencies['direct'].update(pkg_data.get('dependencies', {}))
                    dependencies['dev'].update(pkg_data.get('devDependencies', {}))
                except json.JSONDecodeError:
                    pass
            
            elif file.path.lower() == 'requirements.txt' and file.content:
                for line in file.content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pkg_name = line.split('==')[0].split('>=')[0].split('~=')[0]
                        dependencies['direct'][pkg_name] = line
            
            elif file.path.lower() == 'go.mod' and file.content:
                for line in file.content.split('\n'):
                    if line.strip().startswith('require'):
                        continue
                    if '\t' in line and not line.strip().startswith('//'):
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            dependencies['direct'][parts[0]] = parts[1]
        
        return dependencies
    
    async def _analyze_deployment_requirements(self, repo_data: RepositoryData) -> Dict[str, Any]:
        """Analyze deployment requirements"""
        requirements = {
            'containerization': False,
            'database': [],
            'external_services': [],
            'ports': [],
            'environment_variables': [],
            'volumes': [],
            'scaling_requirements': 'low'
        }
        
        # Check for Docker
        docker_files = ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']
        if any(f.path.lower() in docker_files for f in repo_data.files):
            requirements['containerization'] = True
            
            # Analyze Docker Compose
            compose_file = next((f for f in repo_data.files 
                               if f.path.lower() in ['docker-compose.yml', 'docker-compose.yaml']), None)
            if compose_file and compose_file.content:
                requirements.update(self._analyze_docker_compose(compose_file.content))
        
        # Check for Kubernetes
        k8s_files = [f for f in repo_data.files if f.path.endswith(('.yaml', '.yml')) 
                     and f.content and 'apiversion' in f.content.lower()]
        if k8s_files:
            requirements['orchestration'] = 'kubernetes'
            requirements['scaling_requirements'] = 'high'
        
        # Analyze code for port usage
        for file in repo_data.files:
            if file.content:
                ports = re.findall(r'port[:\s]*(\d+)', file.content, re.IGNORECASE)
                requirements['ports'].extend([int(p) for p in ports if p.isdigit()])
        
        requirements['ports'] = list(set(requirements['ports']))
        return requirements
    
    async def _analyze_security_requirements(self, repo_data: RepositoryData) -> List[str]:
        """Analyze security requirements"""
        security_reqs = []
        
        # Check for authentication patterns
        auth_patterns = [
            r'jwt|jsonwebtoken',
            r'passport|auth0',
            r'oauth|openid',
            r'session|cookie',
            r'bcrypt|scrypt|argon2'
        ]
        
        for file in repo_data.files:
            if file.content:
                content_lower = file.content.lower()
                for pattern in auth_patterns:
                    if re.search(pattern, content_lower):
                        if 'authentication' not in security_reqs:
                            security_reqs.append('authentication')
                        break
        
        # Check for HTTPS/TLS
        https_patterns = [r'https|tls|ssl|cert']
        for file in repo_data.files:
            if file.content:
                for pattern in https_patterns:
                    if re.search(pattern, file.content, re.IGNORECASE):
                        if 'tls_encryption' not in security_reqs:
                            security_reqs.append('tls_encryption')
                        break
        
        # Check for environment variables (secrets)
        env_patterns = [r'\.env|process\.env|os\.environ']
        for file in repo_data.files:
            if file.content:
                for pattern in env_patterns:
                    if re.search(pattern, file.content, re.IGNORECASE):
                        if 'secret_management' not in security_reqs:
                            security_reqs.append('secret_management')
                        break
        
        return security_reqs
    
    async def _analyze_performance_requirements(self, repo_data: RepositoryData) -> Dict[str, Any]:
        """Analyze performance requirements"""
        performance = {
            'caching': False,
            'database_optimization': False,
            'cdn_usage': False,
            'load_balancing': False,
            'estimated_scale': 'small'
        }
        
        # Check for caching
        cache_patterns = [r'redis|memcached|cache', r'@cache|cached']
        for file in repo_data.files:
            if file.content:
                for pattern in cache_patterns:
                    if re.search(pattern, file.content, re.IGNORECASE):
                        performance['caching'] = True
                        break
        
        # Check for database optimization
        db_opt_patterns = [r'index|optimize|query|migration']
        for file in repo_data.files:
            if file.content and file.path.endswith(('.sql', '.py', '.js')):
                for pattern in db_opt_patterns:
                    if re.search(pattern, file.content, re.IGNORECASE):
                        performance['database_optimization'] = True
                        break
        
        # Estimate scale based on complexity
        total_code_lines = sum(len(f.content.split('\n')) for f in repo_data.files 
                              if f.content and f.extension in ['.py', '.js', '.java', '.go'])
        
        if total_code_lines > 10000:
            performance['estimated_scale'] = 'large'
        elif total_code_lines > 5000:
            performance['estimated_scale'] = 'medium'
        else:
            performance['estimated_scale'] = 'small'
        
        return performance
    
    async def _detect_database_usage(self, repo_data: RepositoryData) -> List[str]:
        """Detect database usage patterns"""
        databases = []
        
        db_patterns = {
            r'postgresql|psycopg|pg': 'postgresql',
            r'mysql|pymysql': 'mysql',
            r'mongodb|pymongo': 'mongodb',
            r'redis': 'redis',
            r'sqlite|sqlite3': 'sqlite',
            r'elasticsearch': 'elasticsearch',
            r'cassandra': 'cassandra'
        }
        
        for file in repo_data.files:
            if file.content:
                content_lower = file.content.lower()
                for pattern, db_name in db_patterns.items():
                    if re.search(pattern, content_lower) and db_name not in databases:
                        databases.append(db_name)
        
        return databases
    
    async def _extract_api_endpoints(self, repo_data: RepositoryData) -> List[Dict[str, Any]]:
        """Extract API endpoints from code"""
        endpoints = []
        
        # Patterns for different frameworks
        patterns = {
            'flask': r'@app\.route\([\'"]([^\'\"]+)[\'"].*methods=\[([^\]]+)\]',
            'django': r'path\([\'"]([^\'\"]+)[\'"]',
            'express': r'app\.(get|post|put|delete|patch)\([\'"]([^\'\"]+)[\'"]',
            'fastapi': r'@app\.(get|post|put|delete|patch)\([\'"]([^\'\"]+)[\'"]'
        }
        
        for file in repo_data.files:
            if file.content and file.extension in ['.py', '.js']:
                content = file.content
                
                for framework, pattern in patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        if isinstance(match, tuple):
                            if len(match) == 2:
                                method, path = match
                                endpoints.append({
                                    'path': path,
                                    'method': method.upper(),
                                    'file': file.path,
                                    'framework': framework
                                })
                            else:
                                endpoints.append({
                                    'path': match[0],
                                    'method': 'GET',
                                    'file': file.path,
                                    'framework': framework
                                })
        
        return endpoints
    
    async def _find_environment_variables(self, repo_data: RepositoryData) -> List[str]:
        """Find environment variables used in the project"""
        env_vars = set()
        
        patterns = [
            r'process\.env\.([A-Z_][A-Z0-9_]*)',
            r'os\.environ\.get\([\'"]([A-Z_][A-Z0-9_]*)[\'"]',
            r'os\.getenv\([\'"]([A-Z_][A-Z0-9_]*)[\'"]',
            r'\$\{([A-Z_][A-Z0-9_]*)\}',
            r'\$([A-Z_][A-Z0-9_]*)'
        ]
        
        for file in repo_data.files:
            if file.content:
                for pattern in patterns:
                    matches = re.findall(pattern, file.content)
                    env_vars.update(matches)
        
        # Also check .env files
        env_file = next((f for f in repo_data.files if f.path.endswith('.env')), None)
        if env_file and env_file.content:
            for line in env_file.content.split('\n'):
                if '=' in line and not line.strip().startswith('#'):
                    var_name = line.split('=')[0].strip()
                    env_vars.add(var_name)
        
        return list(env_vars)
    
    async def _detect_build_tools(self, repo_data: RepositoryData) -> List[str]:
        """Detect build tools used in the project"""
        build_tools = []
        
        # Check for specific files
        tool_files = {
            'package.json': 'npm',
            'yarn.lock': 'yarn',
            'pom.xml': 'maven',
            'build.gradle': 'gradle',
            'makefile': 'make',
            'gulpfile.js': 'gulp',
            'webpack.config.js': 'webpack',
            'vite.config.js': 'vite',
            'rollup.config.js': 'rollup'
        }
        
        files = {f.path.lower() for f in repo_data.files}
        for file_pattern, tool in tool_files.items():
            if file_pattern in files:
                build_tools.append(tool)
        
        return build_tools
    
    def _load_framework_patterns(self) -> Dict[str, str]:
        """Load framework detection patterns"""
        return {
            r'from django|import django': 'Django',
            r'from flask|import flask': 'Flask',
            r'from fastapi|import fastapi': 'FastAPI',
            r'import express|require\([\'"]express[\'"]': 'Express.js',
            r'import react|from [\'"]react[\'"]': 'React',
            r'import vue|from [\'"]vue[\'"]': 'Vue.js',
            r'@angular|from [\'"]@angular': 'Angular',
            r'import svelte|from [\'"]svelte[\'"]': 'Svelte',
            r'import next|from [\'"]next[\'"]': 'Next.js',
            r'spring|springframework': 'Spring',
            r'gin-gonic|gin\.': 'Gin',
            r'actix|actix-web': 'Actix',
            r'laravel|illuminate': 'Laravel'
        }
    
    def _load_dependency_patterns(self) -> Dict[str, str]:
        """Load dependency patterns for analysis"""
        return {
            r'axios|fetch|requests': 'http_client',
            r'jwt|jsonwebtoken': 'authentication',
            r'bcrypt|scrypt': 'password_hashing',
            r'redis|cache': 'caching',
            r'postgresql|mysql|mongodb': 'database',
            r'docker|kubernetes': 'containerization'
        }
    
    def _extract_frameworks_from_package(self, file: FileInfo) -> Set[str]:
        """Extract frameworks from package files"""
        frameworks = set()
        
        if file.path.lower() == 'package.json':
            try:
                pkg_data = json.loads(file.content)
                deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
                
                framework_map = {
                    'react': 'React',
                    'vue': 'Vue.js',
                    '@angular/core': 'Angular',
                    'svelte': 'Svelte',
                    'next': 'Next.js',
                    'express': 'Express.js',
                    'koa': 'Koa.js',
                    'fastify': 'Fastify'
                }
                
                for dep in deps:
                    if dep in framework_map:
                        frameworks.add(framework_map[dep])
                        
            except json.JSONDecodeError:
                pass
        
        elif file.path.lower() == 'requirements.txt':
            framework_map = {
                'django': 'Django',
                'flask': 'Flask',
                'fastapi': 'FastAPI',
                'tornado': 'Tornado',
                'pyramid': 'Pyramid'
            }
            
            for line in file.content.split('\n'):
                line = line.strip().lower()
                for dep, framework in framework_map.items():
                    if line.startswith(dep):
                        frameworks.add(framework)
        
        return frameworks
    
    def _analyze_docker_compose(self, content: str) -> Dict[str, Any]:
        """Analyze Docker Compose file"""
        requirements = {}
        
        # Extract services (simplified YAML parsing)
        services = re.findall(r'^\s*([a-zA-Z0-9_-]+):', content, re.MULTILINE)
        if services:
            requirements['services'] = services
        
        # Extract ports
        ports = re.findall(r'ports:.*?(\d+):\d+', content, re.DOTALL)
        if ports:
            requirements['ports'] = [int(p) for p in ports]
        
        # Extract volumes
        volumes = re.findall(r'volumes:.*?- (.+)', content, re.DOTALL)
        if volumes:
            requirements['volumes'] = volumes
        
        return requirements
