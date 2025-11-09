import sys
sys.path.append('..')

from src.document_processor import DocumentProcessor
import json

# Initialize processor
processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)

# Load document
text = processor.load_documents('../data/raw/insurance_policy.txt')
print(f"✅ Loaded document: {len(text)} characters\n")

# Extract sections
sections = processor.extract_sections(text)
print(f"✅ Extracted {len(sections)} sections:")
for section in sections:
    print(f"   - Section {section['section_number']}: {section['title']}")
print()

# Create chunks
chunks = processor.chunk_document(text)
print(f"✅ Created {len(chunks)} chunks\n")

# Validate chunks
is_valid = processor.validate_chunks(chunks)
print(f"✅ Validation: {'PASSED' if is_valid else 'FAILED'}\n")

# Get statistics
stats = processor.get_chunk_statistics(chunks)
print("📊 Statistics:")
for key, value in stats.items():
    print(f"   {key}: {value}")

# Save chunks
with open('../data/processed/chunks.json', 'w') as f:
    json.dump(chunks, f, indent=2)
print("\n✅ Chunks saved to data/processed/chunks.json")

# Preview first chunk
print(f"\n📄 Sample Chunk:")
print(f"ID: {chunks[0]['id']}")
print(f"Section: {chunks[0]['section']}")
print(f"Text preview: {chunks[0]['text'][:200]}...")