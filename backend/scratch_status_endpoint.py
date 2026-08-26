
@router.put("/conversations/{conversation_id}/status")
async def update_conversation_status(
    conversation_id: UUID,
    status_update: ConversationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    business = await db.get(Business, conversation.business_id)
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    if status_update.status not in ["ai_handling", "manual", "needs_human"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    conversation.status = status_update.status
    await db.commit()
    return {"status": "ok", "new_status": conversation.status}
