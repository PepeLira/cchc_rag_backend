from typing import List, Optional
from sqlalchemy.orm import Session
from .document_models import Document, Chunk, Tag

class DocumentController:
	"""
	Controller class for handling Document, Chunk, and Tag creation and retrieval.
	"""

	def __init__(self, db_session: Session):
		"""
		db_session: A SQLAlchemy Session object.
		"""
		self.db_session = db_session

	def commit(self, content):
		self.db_session.add(content)
		self.db_session.commit()
		self.db_session.refresh(content)

		return content

	def create_document(
		self,
		doc_hash: str,
		title: str,
		doc_path: str,
		output_dir: str,
		markdown_path: Optional[str] = None,
		images_path: Optional[str] = None,
		page_count: Optional[int] = None,
		tags: Optional[List[str]] = None,
		chunks: Optional[List[str]] = None,
		auto_commit: bool = False
	) -> Document:
		"""
		Create a new Document. Optionally create Tags from the list of tag names 
		and add text chunks to this document.
		
		:param doc_hash: Unique doc identifier
		:param title: Unique title
		:param doc_path: File path to the document
		:param output_dir: Output directory path
		:param markdown_path: Path to the generated HTML (if any)
		:param images_path: Path to images (if any)
		:param page_count: Number of pages in the document
		:param tags: List of tag names (strings) to link to this document
		:param chunks: Optional list of text for creating Chunk objects
		:return: The created Document object
		"""
		# 1. Create Document
		document = Document(
			doc_hash=doc_hash,
			title=title,
			doc_path=doc_path,
			output_dir=output_dir,
			markdown_path=markdown_path,
			images_path=images_path,
			page_count=page_count,
		)

		# 2. Create and associate Tags, if provided
		if tags:
			# For each tag name, either get it from DB or create a new Tag
			for tag_name in tags:
				tag = self.get_or_create_tag(tag_name)
				document.tags.append(tag)

		# 3. Create and associate Chunks, if provided
		if chunks:
			for chunk_text in chunks:
				chunk = Chunk(
					text=chunk_text,
				)
				document.chunks.append(chunk)

		# 4. Persist in DB
		if auto_commit:
			self.db_session.add(document)
			self.db_session.commit()
			self.db_session.refresh(document)

		return document

	def create_chunk(
		self,
		document_id: int,
		text: str,
		embedding=None,
		page_number: Optional[int] = None,
		auto_commit: bool = False
	) -> Chunk:
		"""
		Create a new Chunk object associated with the given Document ID.

		:param document_id: Existing Document's primary key
		:param text: Chunk text
		:param embedding: Optional embedding data
		:param page_number: Optional page number
		:return: The created Chunk object
		"""
		chunk = Chunk(
			document_id=document_id,
			text=text,
			embedding=embedding,
			page_number=page_number
		)

		if auto_commit:
			self.db_session.add(chunk)
			self.db_session.commit()
			self.db_session.refresh(chunk)
		
		return chunk

	def create_tag(self, tag_name: str, auto_commit: bool = False) -> Tag:
		"""
		Create a new Tag (if it doesn't already exist).
		Raise an exception if a duplicate name is found (since name is unique).
		
		:param tag_name: Name of the tag (unique)
		:return: The created Tag object
		"""
		# This method tries to create a new tag
		# If a duplicate name is inserted, it can raise an integrity error
		tag = Tag(
			name=tag_name
		)
		if auto_commit:
			self.db_session.add(tag)
			self.db_session.commit()
			self.db_session.refresh(tag)
		return tag

	def get_or_create_tag(self, tag_name: str) -> Tag:
		"""
		Get a Tag by name, or create it if it doesn't exist.
		"""
		# Attempt to get a tag with the given name
		tag = self.db_session.query(Tag).filter(Tag.name == tag_name).one_or_none()
		if not tag:
			tag = self.create_tag(tag_name, auto_commit=True)
		return tag

	def get_document_by_id(self, doc_hash: int) -> Optional[Document]:
		"""
		Retrieve a Document by its primary key ID.
		Return None if not found.
		"""
		return self.db_session.query(Document).filter(Document.id == doc_hash).one_or_none()

	def get_document_by_title(self, title: str) -> Optional[Document]:
		"""
		Retrieve a Document by its unique title.
		Return None if not found.
		"""
		return self.db_session.query(Document).filter(Document.title == title).one_or_none()

	def get_chunk_by_id(self, chunk_id: int) -> Optional[Chunk]:
		"""
		Retrieve a Chunk by its primary key ID.
		"""
		return self.db_session.query(Chunk).filter(Chunk.id == chunk_id).one_or_none()

	def list_documents(self) -> List[Document]:
		"""
		List all documents.
		"""
		return self.db_session.query(Document).all()

	def list_tags(self) -> List[Tag]:
		"""
		List all tags.
		"""
		return self.db_session.query(Tag).all()

	def add_tag_to_document(self, document: Document, tag_name: str) -> Document:
		"""
		Associate a tag with a specific document (by object reference).
		"""
		tag = self.get_or_create_tag(tag_name)
		if tag not in document.tags:
			document.tags.append(tag)
			self.db_session.commit()
			self.db_session.refresh(document)
		return document

	def add_tag_to_document_by_id(self, document_id: int, tag_name: str) -> Document:
		"""
		Associate a tag with a specific document by document_id.
		"""
		document = self.get_document_by_id(document_id)
		if not document:
			raise ValueError(f"Document with id={document_id} not found.")
		return self.add_tag_to_document(document, tag_name)
	
	def delete_all_documents(self):
		"""
		Delete all documents.
		"""
		self.db_session.query(Document).delete()
		self.db_session.commit()
