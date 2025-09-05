import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.solar_api.domain.panel_model import (
    PanelModel,
    PanelModelCreate,
    PanelModelUpdate,
)
from src.solar_api.application.ports.panel_repository import PanelRepositoryPort


class JSONPanelRepository(PanelRepositoryPort):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        path = Path(self.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"models": []}, f, indent=2, ensure_ascii=False)

    def _read_data(self) -> Dict[str, Any]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_data(self, data: Dict[str, Any]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def get_all(self) -> List[PanelModel]:
        data = self._read_data()
        return [PanelModel(**model) for model in data.get("models", [])]

    async def get_by_id(self, model_id: str) -> Optional[PanelModel]:
        data = self._read_data()
        for model in data.get("models", []):
            if model["id"] == model_id:
                return PanelModel(**model)
        return None

    async def create(self, panel: PanelModelCreate) -> PanelModel:
        data = self._read_data()
        new_id = str(uuid.uuid4())
        new_panel = PanelModel(id=new_id, **panel.model_dump())
        data["models"].append(new_panel.model_dump())
        self._write_data(data)
        return new_panel

    async def update(
        self, model_id: str, panel_update: PanelModelUpdate
    ) -> Optional[PanelModel]:
        data = self._read_data()
        for i, model in enumerate(data["models"]):
            if model["id"] == model_id:
                updated_data = model.copy()
                update_data = panel_update.model_dump(exclude_unset=True)
                updated_data.update(update_data)
                updated_panel = PanelModel(**updated_data)
                data["models"][i] = updated_panel.model_dump()
                self._write_data(data)
                return updated_panel
        return None

    async def delete(self, model_id: str) -> bool:
        data = self._read_data()
        initial_length = len(data["models"])
        data["models"] = [m for m in data["models"] if m["id"] != model_id]

        if len(data["models"]) < initial_length:
            self._write_data(data)
            return True
        return False
