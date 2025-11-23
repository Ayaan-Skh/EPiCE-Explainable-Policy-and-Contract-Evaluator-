from typing import List, Dict, Optional
import re
import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.logger import logging
from src.exception import CustomException

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]  # Added ". " for better sentence splitting
        )
        
    def load_documents(self, file_path: str) -> str:
        """Load document from file path"""
        try:
            with open(file=file_path, mode='r', encoding='utf-8') as file:
                text = file.read()
            logging.info(f"Successfully loaded document from {file_path}")
            return text    
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            raise CustomException(sys, f"File not found: {file_path}")
        except Exception as e:
            raise CustomException(sys, e)    
            
    def extract_sections(self, text: str) -> List[Dict]:
        """Extract sections from policy document"""
        try:
            # Fixed pattern - removed invalid regex syntax
            # This pattern captures from "SECTION X:" until next section or end
            pattern = r'SECTION\s+(\d+):\s+([A-Z\s]+)\s*\n(.*?)(?=SECTION\s+\d+:|$)'
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            
            sections = []
            for i, match in enumerate(matches):
                section_number = match[0]  # First capture group
                title = match[1].strip()    # Second capture group
                content = match[2].strip()  # Third capture group
                
                sections.append({
                    "section_number": section_number,
                    "title": title,
                    "content": content
                })
                logging.info(f"Extracted Section {section_number}: {title}")
                logging.info(f"Content preview: {content[:100]}...")
            
            return sections
        except Exception as e:
            logging.error(f"Error extracting sections: {str(e)}")
            raise CustomException(sys, e)       
    
    def chunk_document(self, text: str) -> List[Dict]:
        """
        Split document into chunks with metadata.
        
        Returns:
            List[Dict]: Each dict contains:
                - id: unique identifier (chunk_0, chunk_1, etc.)
                - text: chunk content
                - section: section title/name
                - chunk_index: position in document
                - char_start: starting character position
                - char_end: ending character position
        """
        try:
            # Step 1: Split text into chunks
            split_texts = self.text_splitter.split_text(text)
            logging.info(f"Document split into {len(split_texts)} chunks")
            
            chunks = []
            current_position = 0
            
            # Step 2: Add metadata to each chunk
            for idx, chunk_text in enumerate(split_texts):
                # Find the position of this chunk in the original text
                chunk_start = text.find(chunk_text, current_position)
                
                # Handle case where exact match not found (due to processing)
                if chunk_start == -1:
                    chunk_start = current_position
                
                chunk_end = chunk_start + len(chunk_text)
                
                # Step 3: Identify which section this chunk belongs to
                section_name = self._identify_section(chunk_text, text, chunk_start)
                
                # Create chunk dictionary with metadata
                chunk_dict = {
                    "id": f"chunk_{idx}",
                    "text": chunk_text,
                    "section": section_name,
                    "chunk_index": idx,
                    "char_start": chunk_start,
                    "char_end": chunk_end
                }
                
                chunks.append(chunk_dict)
                current_position = chunk_end
                
                logging.info(f"Created chunk {idx}: section='{section_name}', length={len(chunk_text)}")
            
            return chunks
            
        except Exception as e:
            logging.error(f"Error chunking document: {str(e)}")
            raise CustomException(sys, e)
        
    def _identify_section(self, chunk: str, full_text: str, chunk_start: int) -> str:
        """
        Identify which section a chunk belongs to based on its position in the full text.
        
        Logic:
        1. Find all section headers and their positions
        2. Determine which section the chunk falls under based on character position
        3. Return the section title
        
        Args:
            chunk: The text chunk to identify
            full_text: The complete document text
            chunk_start: Starting position of chunk in full_text
            
        Returns:
            str: Section title or "General" if no section found
        """
        try:
            # Find all section headers with their positions
            pattern = r'SECTION\s+(\d+):\s+([A-Z\s]+)'
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            
            # Store sections with their start positions
            sections_positions = []
            for match in matches:
                section_number = match.group(1)
                section_title = match.group(2).strip()
                section_start = match.start()
                
                sections_positions.append({
                    'number': section_number,
                    'title': section_title,
                    'start': section_start
                })
            
            # Sort by position (should already be sorted, but just in case)
            sections_positions.sort(key=lambda x: x['start'])
            
            # Find which section this chunk belongs to
            # The chunk belongs to the last section that starts before the chunk
            current_section = "General"  # Default if no section found
            
            for section in sections_positions:
                if section['start'] <= chunk_start:
                    current_section = section['title']
                else:
                    # We've passed the chunk's position
                    break
            
            return current_section
            
        except Exception as e:
            logging.error(f"Error identifying section: {str(e)}")
            # Return default section name instead of failing
            return "General"
            
    def validate_chunks(self, chunks: List[Dict]) -> bool:
        """
        Validate that chunks have required metadata and reasonable content.
        
        Checks:
        - All required fields present
        - No empty chunks
        - Reasonable length distribution
        """
        try:
            if not chunks:
                logging.error("No chunks to validate")
                return False
            
            required_keys = ["id", "text", "section", "chunk_index", "char_start", "char_end"]
            
            for i, chunk in enumerate(chunks):
                # Check all required keys present
                if not all(key in chunk for key in required_keys):
                    missing_keys = [key for key in required_keys if key not in chunk]
                    logging.error(f"Chunk {i} missing metadata: {missing_keys}")
                    return False
                
                # Check chunk is not empty
                if not chunk['text'] or len(chunk['text'].strip()) == 0:
                    logging.error(f"Chunk {i} has empty text")
                    return False
                
                # Check chunk has reasonable length (not too short)
                if len(chunk['text']) < 50:
                    logging.warning(f"Chunk {i} is very short: {len(chunk['text'])} characters")
                
                # Check char_end > char_start
                if chunk['char_end'] <= chunk['char_start']:
                    logging.error(f"Chunk {i} has invalid character positions")
                    return False
            
            # Check chunk indices are sequential
            for i, chunk in enumerate(chunks):
                if chunk['chunk_index'] != i:
                    logging.error(f"Chunk indices not sequential at position {i}")
                    return False
            
            logging.info(f"All {len(chunks)} chunks validated successfully.")
            logging.info(f"Average chunk length: {sum(len(c['text']) for c in chunks) / len(chunks):.0f} characters")
            
            return True
            
        except Exception as e:
            logging.error(f"Error validating chunks: {str(e)}")
            raise CustomException(sys, e)
    
    def get_chunk_statistics(self, chunks: List[Dict]) -> Dict:
        """
        Get statistics about the chunks for quality assessment.
        
        Returns:
            Dict with statistics: count, avg_length, sections_covered, etc.
        """
        try:
            if not chunks:
                return {}
            
            chunk_lengths = [len(chunk['text']) for chunk in chunks]
            sections = set(chunk['section'] for chunk in chunks)
            
            stats = {
                'total_chunks': len(chunks),
                'avg_chunk_length': sum(chunk_lengths) / len(chunks),
                'min_chunk_length': min(chunk_lengths),
                'max_chunk_length': max(chunk_lengths),
                'unique_sections': len(sections),
                'sections_covered': list(sections)
            }
            
            logging.info(f"Chunk statistics: {stats}")
            return stats
            
        except Exception as e:
            logging.error(f"Error calculating statistics: {str(e)}")
            return {}