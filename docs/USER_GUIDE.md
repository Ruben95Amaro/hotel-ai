# User Guide

## What is Hotel AI Assistant?

Hotel AI Assistant is being developed to help hotel guests find information by asking questions in everyday language. Rather than browsing multiple documents, a guest can ask a direct question and receive a concise answer based on the hotel's available information.

## Example use cases

Guests may use the assistant to ask about:

- Check-in and check-out times.
- Reception availability.
- Pet policies.
- Cancellation rules.
- Hotel facilities and services, once those details are added to the knowledge base.

See [Conversation Examples](CONVERSATION_EXAMPLES.md) for sample interactions.

## How a guest would use it

The intended experience is simple:

1. Open the hotel's chat interface.
2. Type a question in natural language.
3. Receive an answer based on the hotel's information.
4. If the information is unavailable or unclear, receive a transparent message rather than an invented policy.

A guest-facing interface has not yet been confirmed as implemented. At the current development stage, the API is the main interaction point.

## Current limitations

- The assistant can only answer reliably about information included in its knowledge base and retrieved correctly.
- Example answers in the documentation describe the intended behaviour; they are not a guarantee that every conversation works end to end today.
- Booking changes, payments, room availability, and requests requiring access to hotel systems are outside the current implemented scope.
- If the assistant cannot find enough relevant information, it should say so and direct the guest to hotel staff.
