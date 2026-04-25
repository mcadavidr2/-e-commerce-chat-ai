import pytest
from datetime import datetime
from domain.entities import Product, ChatMessage, ChatContext


# --- Fixtures ---

@pytest.fixture
def valid_product():
    return Product(
        id=1, name="Air Max", brand="Nike", category="Running",
        size="42", color="Negro", price=150.0, stock=10,
        description="Zapatilla de running"
    )

@pytest.fixture
def valid_message():
    return ChatMessage(
        id=1, session_id="abc123", role="user",
        message="Hola", timestamp=datetime.utcnow()
    )


# --- Product validaciones ---

class TestProductValidations:
    def test_price_must_be_positive(self):
        with pytest.raises(ValueError, match="precio"):
            Product(id=None, name="X", brand="B", category="C",
                    size="40", color="N", price=0, stock=5, description="D")

    def test_negative_price_raises(self):
        with pytest.raises(ValueError):
            Product(id=None, name="X", brand="B", category="C",
                    size="40", color="N", price=-10, stock=5, description="D")

    def test_negative_stock_raises(self):
        with pytest.raises(ValueError, match="stock"):
            Product(id=None, name="X", brand="B", category="C",
                    size="40", color="N", price=100, stock=-1, description="D")

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="nombre"):
            Product(id=None, name="  ", brand="B", category="C",
                    size="40", color="N", price=100, stock=5, description="D")

    def test_valid_product_created(self, valid_product):
        assert valid_product.name == "Air Max"
        assert valid_product.price == 150.0


# --- Product métodos ---

class TestProductMethods:
    def test_is_available_with_stock(self, valid_product):
        assert valid_product.is_available() is True

    def test_is_available_without_stock(self, valid_product):
        valid_product.stock = 0
        assert valid_product.is_available() is False

    def test_reduce_stock(self, valid_product):
        valid_product.reduce_stock(3)
        assert valid_product.stock == 7

    def test_reduce_stock_insufficient(self, valid_product):
        with pytest.raises(ValueError, match="insuficiente"):
            valid_product.reduce_stock(99)

    def test_reduce_stock_negative_quantity(self, valid_product):
        with pytest.raises(ValueError):
            valid_product.reduce_stock(-1)

    def test_increase_stock(self, valid_product):
        valid_product.increase_stock(5)
        assert valid_product.stock == 15

    def test_increase_stock_negative_quantity(self, valid_product):
        with pytest.raises(ValueError):
            valid_product.increase_stock(0)


# --- ChatMessage validaciones ---

class TestChatMessageValidations:
    def test_invalid_role_raises(self):
        with pytest.raises(ValueError, match="rol"):
            ChatMessage(id=None, session_id="abc", role="admin",
                        message="Hola", timestamp=datetime.utcnow())

    def test_empty_message_raises(self):
        with pytest.raises(ValueError, match="mensaje"):
            ChatMessage(id=None, session_id="abc", role="user",
                        message="  ", timestamp=datetime.utcnow())

    def test_empty_session_id_raises(self):
        with pytest.raises(ValueError, match="session_id"):
            ChatMessage(id=None, session_id="", role="user",
                        message="Hola", timestamp=datetime.utcnow())

    def test_is_from_user(self, valid_message):
        assert valid_message.is_from_user() is True
        assert valid_message.is_from_assistant() is False

    def test_is_from_assistant(self):
        msg = ChatMessage(id=None, session_id="abc", role="assistant",
                          message="Hola", timestamp=datetime.utcnow())
        assert msg.is_from_assistant() is True
        assert msg.is_from_user() is False


# --- ChatContext ---

class TestChatContext:
    def test_format_for_prompt(self):
        messages = [
            ChatMessage(id=1, session_id="s1", role="user",
                        message="Quiero zapatillas", timestamp=datetime.utcnow()),
            ChatMessage(id=2, session_id="s1", role="assistant",
                        message="¿Qué talla usas?", timestamp=datetime.utcnow()),
        ]
        context = ChatContext(messages=messages)
        result = context.format_for_prompt()
        assert "Usuario: Quiero zapatillas" in result
        assert "Asistente: ¿Qué talla usas?" in result

    def test_get_recent_messages_limit(self):
        messages = [
            ChatMessage(id=i, session_id="s1", role="user",
                        message=f"msg {i}", timestamp=datetime.utcnow())
            for i in range(10)
        ]
        context = ChatContext(messages=messages, max_messages=6)
        recent = context.get_recent_messages()
        assert len(recent) == 6
        assert recent[-1].message == "msg 9"

    def test_get_recent_messages_less_than_max(self):
        messages = [
            ChatMessage(id=1, session_id="s1", role="user",
                        message="solo uno", timestamp=datetime.utcnow())
        ]
        context = ChatContext(messages=messages, max_messages=6)
        assert len(context.get_recent_messages()) == 1