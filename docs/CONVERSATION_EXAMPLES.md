# Conversation Examples

These examples illustrate the intended guest experience. They are sample scenarios, not proof that every answer is already validated in the live API. The exact answer should always match the current hotel's approved information.

## 1. Check-in time

**Guest:** What time can I check in?

**Assistant:** Check-in starts at 15:00.

**Why this is useful:** The assistant retrieves a specific policy from the hotel information instead of guessing.

## 2. Check-out time

**Guest:** What time do I need to check out?

**Assistant:** Check-out is until 11:00.

## 3. Reception availability

**Guest:** Is reception open at night?

**Assistant:** Yes. Reception is open 24 hours a day.

## 4. Travelling with a pet

**Guest:** Can I bring my dog?

**Assistant:** Pets are allowed in selected rooms. Please contact the hotel to confirm whether a suitable room is available for your stay.

**Why this is useful:** The answer preserves the policy's limitation instead of promising that every room accepts pets.

## 5. Cancellation policy

**Guest:** Can I cancel my booking for free?

**Assistant:** The hotel information states that cancellation is free up to 48 hours before arrival. Please check your booking conditions to confirm how this applies to your reservation.

## 6. Information not available

**Guest:** Does the hotel have an airport shuttle?

**Assistant:** I couldn't find confirmed information about an airport shuttle. Please contact the hotel reception to confirm.

**Why this is useful:** The assistant should not invent services when the knowledge base does not contain an answer.

## 7. A broader question

**Guest:** What should I know before arriving?

**Assistant:** Check-in starts at 15:00, check-out is until 11:00, and reception is open 24 hours a day. Pets are allowed in selected rooms. If you have a specific question about your booking, I can help look for the relevant hotel information.

**Note:** This response is appropriate only if each detail is present in the retrieved hotel context.

## Product principle

The assistant should be concise, polite, and transparent. When it cannot find reliable information, it should say so instead of fabricating an answer. Any answer involving a reservation or an individual booking should be confirmed by the hotel's official systems or staff.
