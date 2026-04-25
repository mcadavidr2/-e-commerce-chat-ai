import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime
from domain.entities import Product
from domain.exceptions import ProductNotFoundError
from application.product_service import ProductService
from application.chat_service import ChatService
from application.dtos import ChatMessageRequestDTO


# --- Fixtures ---

@pytest.fixture
def sample_product():
    return Product(
        id=1, name="Air Max", brand="Nike", category="Running",
        size="42", color="Negro", price=150.0, stock=10,
        description="Zapatilla de running"
    )

@pytest.fixture
def mock_product_repo(sample_product):
    repo = MagicMock()
    repo.get_all.return_value = [sample_product]
    repo.get_by_id.return_value = sample_product
    repo.save.return_value = sample_product
    repo.delete.return_value = True
    return repo

@pytest.fixture
def product_service(mock_product_repo):
    return ProductService(mock_product_repo)


# --- ProductService ---

class TestProductService:
    def test_get_all_products(self, product_service, mock_product_repo):
        result = product_service.get_all_products()
        assert len(result) == 1
        assert result[0].name == "Air Max"
        mock_product_repo.get_all.assert_called_once()

    def test_get_product_by_id(self, product_service):
        result = product_service.get_product_by_id(1)
        assert result.id == 1

    def test_get_product_by_id_not_found(self, product_service, mock_product_repo):
        mock_product_repo.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError):
            product_service.get_product_by_id(99)

    def test_delete_product(self, product_service, mock_product_repo):
        result = product_service.delete_product(1)
        assert result is True
        mock_product_repo.delete.assert_called_once_with(1)

    def test_delete_product_not_found(self, product_service, mock_product_repo):
        mock_product_repo.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError):
            product_service.delete_product(99)

    def test_get_available_products(self, product_service, mock_product_repo, sample_product):
        out_of_stock = Product(
            id=2, name="Old Skool", brand="Vans", category="Casual",
            size="40", color="Negro", price=80.0, stock=0,
            description="Sin stock"
        )
        mock_product_repo.get_all.return_value = [sample_product, out_of_stock]
        result = product_service.get_available_products()
        assert len(result) == 1
        assert result[0].name == "Air Max"


# --- ChatService ---

class TestChatService:
    @pytest.fixture
    def mock_chat_repo(self):
        repo = MagicMock()
        repo.get_recent_messages.return_value = []
        repo.save_message.side_effect = lambda msg: msg
        return repo

    @pytest.fixture
    def mock_ai_service(self):
        ai = MagicMock()
        ai.generate_response = AsyncMock(return_value="Te recomiendo las Air Max.")
        return ai

    @pytest.fixture
    def chat_service(self, mock_product_repo, mock_chat_repo, mock_ai_service):
        return ChatService(
            product_repository=mock_product_repo,
            chat_repository=mock_chat_repo,
            ai_service=mock_ai_service,
        )

    @pytest.mark.asyncio
    async def test_process_message(self, chat_service, mock_ai_service):
        request = ChatMessageRequestDTO(session_id="s1", message="Quiero zapatillas Nike")
        response = await chat_service.process_message(request)
        assert response.assistant_message == "Te recomiendo las Air Max."
        assert response.session_id == "s1"
        mock_ai_service.generate_response.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_process_message_saves_both_messages(self, chat_service, mock_chat_repo):
        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        await chat_service.process_message(request)
        assert mock_chat_repo.save_message.call_count == 2

    def test_get_session_history(self, chat_service, mock_chat_repo):
        chat_service.get_session_history("s1", limit=5)
        mock_chat_repo.get_session_history.assert_called_once_with("s1", limit=5)

    def test_clear_session_history(self, chat_service, mock_chat_repo):
        mock_chat_repo.delete_session_history.return_value = 4
        result = chat_service.clear_session_history("s1")
        assert result == 4