
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import User, Conversation, Message


def test_database_operations():
    with SessionLocal() as db:
        try:
            # 1. Create user
            user = User(
                username="her_test_user",
                email="her_test@example.com"
            )

            db.add(user)
            db.flush()

            # 2. Create conversation
            conversation = Conversation(
                user_id=user.id,
                title="My first conversation with HER"
            )

            db.add(conversation)
            db.flush()

            # 3. Save user message
            user_message = Message(
                conversation_id=conversation.id,
                role="user",
                content="I want to become an AI engineer."
            )

            # 4. Save HER response
            her_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content="Let's work towards that goal together!"
            )

            db.add_all([user_message, her_message])

            # Commit everything
            db.commit()

            print("USER CREATED:", user.id)
            print("CONVERSATION CREATED:", conversation.id)

            # 5. Retrieve conversation history
            messages = db.scalars(
                select(Message)
                .where(Message.conversation_id == conversation.id)
                .order_by(Message.created_at)
            ).all()

            print("\nCONVERSATION HISTORY:")

            for message in messages:
                print(f"{message.role}: {message.content}")

            assert len(messages) == 2

            print("\nDATABASE OPERATIONS SUCCESSFUL!")

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    test_database_operations()
