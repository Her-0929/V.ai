
from uuid import UUID

from app.core.database import SessionLocal
from app.services.conversation_service import conversation_service


def test_conversation():

    user_id = UUID(
        "35d636d9-fa44-4e92-9ecd-2e39a9194559"
    )

    db = SessionLocal()

    try:
        # 1. Create conversation
        conversation = conversation_service.create_conversation(
            db=db,
            user_id=user_id,
            title="Getting to know HER"
        )

        print("\nCONVERSATION CREATED:", conversation.id)

        # 2. Save user message
        conversation_service.save_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            role="user",
            content="I want to become an AI engineer."
        )

        # 3. Save HER response
        conversation_service.save_message(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            role="assistant",
            content="That's a great goal! Let's work towards it together."
        )

        # 4. Retrieve conversation history
        history = conversation_service.get_conversation_history(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id
        )

        print("\nCONVERSATION HISTORY:")

        for message in history:
            print(f"{message['role']}: {message['content']}")

        # 5. List user conversations
        conversations = conversation_service.get_user_conversations(
            db=db,
            user_id=user_id
        )

        print("\nTOTAL CONVERSATIONS:", len(conversations))

        print("\nHER CONVERSATION PERSISTENCE SUCCESSFUL!")

    finally:
        db.close()


if __name__ == "__main__":
    test_conversation()
