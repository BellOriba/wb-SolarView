from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.solar_api.domain.panel_model import (
    PanelModel,
    PanelModelCreate,
    PanelModelUpdate,
)
from src.solar_api.database.models import PanelModel as PanelModelDB
from src.solar_api.application.ports.panel_repository import PanelRepositoryPort


class PostgresPanelRepository(PanelRepositoryPort):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_all(self, user_id: int) -> List[PanelModel]:
        result = await self.db.execute(
            select(PanelModelDB)
            .where(PanelModelDB.user_id == user_id)
            .order_by(PanelModelDB.name)
        )
        panels = result.scalars().all()
        return [PanelModel.model_validate(panel.to_dict()) for panel in panels]

    async def get_by_id(self, model_id: UUID, user_id: int) -> Optional[PanelModel]:
        result = await self.db.execute(
            select(PanelModelDB).where(
                and_(PanelModelDB.id == model_id, PanelModelDB.user_id == user_id)
            )
        )
        panel = result.scalars().first()
        return PanelModel.model_validate(panel.to_dict()) if panel else None

    async def create(self, panel: PanelModelCreate, user_id: int) -> PanelModel:
        db_panel = PanelModelDB(
            name=panel.name,
            capacity=panel.capacity,
            efficiency=panel.efficiency,
            manufacturer=panel.manufacturer,
            type=panel.type,
            user_id=user_id,
        )

        self.db.add(db_panel)
        await self.db.commit()
        await self.db.refresh(db_panel)

        return PanelModel.model_validate(db_panel.to_dict())

    async def update(
        self, model_id: UUID, panel_update: PanelModelUpdate, user_id: int
    ) -> Optional[PanelModel]:
        update_data = panel_update.model_dump(exclude_unset=True)

        stmt = (
            update(PanelModelDB)
            .where(and_(PanelModelDB.id == model_id, PanelModelDB.user_id == user_id))
            .values(**update_data, updated_at=func.now())
            .returning(PanelModelDB)
        )

        result = await self.db.execute(stmt)
        updated_panel = result.scalars().first()

        if updated_panel:
            await self.db.commit()
            await self.db.refresh(updated_panel)
            return PanelModel.model_validate(updated_panel.to_dict())

        return None

    async def delete(self, model_id: UUID, user_id: int) -> bool:
        stmt = delete(PanelModelDB).where(
            and_(PanelModelDB.id == model_id, PanelModelDB.user_id == user_id)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount > 0
