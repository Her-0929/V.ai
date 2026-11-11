from sqlalchemy import select
from app.core.database import SessionLocal
from app.models import (
    User,
    Conversation,
    Message,
    Memory,
    MemorySource,
    UserPreference
)


def test_memory_operations():

    with SessionLocal() as db:
        try:
            # 1. Retrieve existing test user
            user = db.scalar(
                select(User).where(
                    User.email == "her_test@example.com"
                )
            )

            if not user:
                raise ValueError("Test user not found")

            # 2. Retrieve existing conversation
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.user_id == user.id
                )
            )

            if not conversation:
                raise ValueError("Conversation not found")

            # 3. Retrieve original user message
            message = db.scalar(
                select(Message).where(
                    Message.conversation_id == conversation.id,
                    Message.role == "user"
                )
            )

            if not message:
                raise ValueError("User message not found")

            # 4. Create long-term memory
            memory = Memory(
                user_id=user.id,
                memory_type="career_goal",
                content="User wants to become an AI engineer",
                importance=5,
                confidence=1.0,
                is_active=True
            )

            db.add(memory)
            db.flush()

            # 5. Connect memory to its original message
            source = MemorySource(
                memory_id=memory.id,
                message_id=message.id,
                source_type="message",
                excerpt=message.content
            )

            db.add(source)

            # 6. Save a user preference
            preference = db.scalar(
                select(UserPreference).where(
                    UserPreference.user_id == user.id,
                    UserPreference.key == "response_style"
                )
            )

            if preference:
                preference.value = {"style": "detailed"}
            else:
                preference = UserPreference(
                    user_id=user.id,
                    key="response_style",
                    value={"style": "detailed"}
                )
                db.add(preference)

            db.commit()

            print("\nHER MEMORY TEST SUCCESSFUL!")
            print("Memory:", memory.content)
            print("Memory type:", memory.memory_type)
            print("Importance:", memory.importance)
            print("Original message:", source.excerpt)
            print("Preference:", preference.value)

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    test_memory_operations()
