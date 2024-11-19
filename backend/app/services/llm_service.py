# backend/app/services/llm_service.py

from typing import List, Dict, Any
import openai
import json
from ..core.config import settings
from fastapi import HTTPException

class LLMService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE

    async def analyze_code(
        self,
        code: str,
        file_path: str,
        diff: str = None
    ) -> List[Dict[str, Any]]:
        """Analyze code and generate suggestions"""
        try:
            # Prepare the prompt
            prompt = self._build_analysis_prompt(code, file_path, diff)
            
            # Get completion from OpenAI
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse suggestions from response
            suggestions = self._parse_suggestions(
                response.choices[0].message.content
            )
            
            return suggestions
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze code: {str(e)}"
            )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for code analysis"""
        return """You are an expert code reviewer with deep knowledge of software engineering best practices, security, and performance optimization. Analyze the provided code and suggest improvements in the following areas:
        1. Code quality and maintainability
        2. Security vulnerabilities
        3. Performance optimizations
        4. Style and consistency
        
        Provide specific, actionable suggestions with explanations and example code."""

    def _build_analysis_prompt(
        self,
        code: str,
        file_path: str,
        diff: str = None
    ) -> str:
        """Build the analysis prompt"""
        prompt = f"Review the following code from {file_path}:\n\n{code}\n\n"
        if diff:
            prompt += f"Changes made in this PR:\n\n{diff}\n\n"
        prompt += """Provide analysis and suggestions in the following JSON format:
        {
            "suggestions": [
                {
                    "type": "improvement|security|performance|style",
                    "message": "Brief description of the issue",
                    "line_start": line_number,
                    "line_end": line_number,
                    "original_code": "The problematic code",
                    "suggested_code": "The improved code",
                    "explanation": "Detailed explanation of the suggestion",
                    "confidence": confidence_score_between_0_and_1
                }
            ]
        }"""
        return prompt

    def _parse_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """Parse and validate the LLM response"""
        try:
            data = json.loads(response)
            suggestions = data.get("suggestions", [])
            
            # Validate each suggestion
            validated_suggestions = []
            for suggestion in suggestions:
                if all(k in suggestion for k in [
                    "type", "message", "line_start", "line_end",
                    "original_code", "suggested_code", "explanation", "confidence"
                ]):
                    # Validate suggestion type
                    if suggestion["type"] not in [
                        "improvement", "security", "performance", "style"
                    ]:
                        continue
                    
                    # Validate confidence score
                    suggestion["confidence"] = float(suggestion["confidence"])
                    if not 0 <= suggestion["confidence"] <= 1:
                        continue
                    
                    validated_suggestions.append(suggestion)
            
            return validated_suggestions
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse LLM response: {str(e)}"
            )

    async def analyze_code_style(
        self,
        code: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """Analyze code style and consistency"""
        prompt = f"""Analyze the following {language} code for style issues and consistency:

        {code}

        Focus on:
        1. Naming conventions
        2. Code formatting
        3. Documentation
        4. Consistency with language best practices"""
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for style analysis
            max_tokens=self.max_tokens
        )
        
        return self._parse_suggestions(response.choices[0].message.content)

    async def analyze_security(
        self,
        code: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """Analyze code for security vulnerabilities"""
        prompt = f"""Analyze the following {language} code for security vulnerabilities:

        {code}

        Focus on:
        1. Input validation
        2. Authentication/Authorization
        3. Data validation
        4. Common security pitfalls
        5. Secure coding practices"""
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for security analysis
            max_tokens=self.max_tokens
        )
        
        return self._parse_suggestions(response.choices[0].message.content)

    async def analyze_performance(
        self,
        code: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """Analyze code for performance optimization opportunities"""
        prompt = f"""Analyze the following {language} code for performance optimizations:

        {code}

        Focus on:
        1. Algorithmic efficiency
        2. Resource usage
        3. Memory management
        4. Caching opportunities
        5. Common performance pitfalls"""
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=self.max_tokens
        )
        
        return self._parse_suggestions(response.choices[0].message.content)

    async def generate_review_summary(
        self,
        suggestions: List[Dict[str, Any]]
    ) -> str:
        """Generate a human-readable summary of the review"""
        prompt = f"""Generate a concise summary of the following code review suggestions:

        {suggestions}

        Include:
        1. Overview of main findings
        2. Key areas for improvement
        3. Priority recommendations"""
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical writer creating clear, concise code review summaries."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    async def suggest_tests(
        self,
        code: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """Suggest test cases for the code"""
        prompt = f"""Analyze the following {language} code and suggest test cases:

        {code}

        Focus on:
        1. Unit tests for key functionality
        2. Edge cases
        3. Error scenarios
        4. Integration test scenarios
        
        Provide suggestions in the standard JSON format."""
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a testing expert focusing on comprehensive test coverage."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=self.max_tokens
        )
        
        return self._parse_suggestions(response.choices[0].message.content)

    async def explain_changes(
        self,
        diff: str,
        context: str = None
    ) -> str:
        """Generate a human-readable explanation of code changes"""
        prompt = f"""Explain the following code changes in a clear, concise manner:

        {diff}
        
        {f'Context: {context}' if context else ''}
        
        Focus on:
        1. What changed
        2. Why it matters
        3. Potential impacts"""
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical writer explaining code changes to developers."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content