from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import List
from database import get_session
from modelos.adotante import Adotante, AdotanteBase

router = APIRouter(prefix="/adotantes", tags=["Adotantes"])

# --- CREATE ---
@router.post("/", response_model=Adotante, status_code=201)
def criar_adotante(adotante: AdotanteBase, session: Session = Depends(get_session)):
    db_adotante = Adotante.model_validate(adotante)
    session.add(db_adotante)
    try:
        session.commit()
        session.refresh(db_adotante)
        return db_adotante
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar adotante: {e}")

# --- READ (Listar com Filtro de Nome) ---
@router.get("/", response_model=List[Adotante])
def listar_adotantes(
    session: Session = Depends(get_session),
    nome: str | None = Query(None, description="Filtrar por nome parcial")
):
    query = select(Adotante)
    
    if nome:
        query = query.where(func.lower(Adotante.nome).contains(nome.lower()))
        
    return session.exec(query).all()

# --- READ (Por ID)---
@router.get("/{adotante_id}", response_model=Adotante)
def obter_adotante(adotante_id: int, session: Session = Depends(get_session)):
    adotante = session.get(Adotante, adotante_id)
    if not adotante:
        raise HTTPException(status_code=404, detail="Adotante não encontrado")
    return adotante

# --- UPDATE ---
@router.patch("/{adotante_id}", response_model=Adotante)
def atualizar_adotante(adotante_id: int, adotante_data: AdotanteBase, session: Session = Depends(get_session)):
    db_adotante = session.get(Adotante, adotante_id)
    if not db_adotante:
        raise HTTPException(status_code=404, detail="Adotante não encontrado")
    
    dados = adotante_data.model_dump(exclude_unset=True)
    for key, value in dados.items():
        setattr(db_adotante, key, value)

    session.add(db_adotante)
    session.commit()
    session.refresh(db_adotante)
    return db_adotante

# --- DELETE ---
@router.delete("/{adotante_id}")
def deletar_adotante(adotante_id: int, session: Session = Depends(get_session)):
    db_adotante = session.get(Adotante, adotante_id)
    if not db_adotante:
        raise HTTPException(status_code=404, detail="Adotante não encontrado")
    
    session.delete(db_adotante)
    session.commit()
    return {"message": "Adotante removido com sucesso"}