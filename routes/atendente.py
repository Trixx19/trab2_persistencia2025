from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import List
from database import get_session
from modelos.atendente import Atendente, AtendenteBase

router = APIRouter(prefix="/atendentes", tags=["Atendentes"])

# --- CREATE ---
@router.post("/", response_model=Atendente, status_code=201)
def criar_atendente(atendente: AtendenteBase, session: Session = Depends(get_session)):
    db_atendente = Atendente.model_validate(atendente)
    session.add(db_atendente)
    try:
        session.commit()
        session.refresh(db_atendente)
        return db_atendente
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar atendente: {e}")

# --- READ (Listar com Filtro de Nome) ---
@router.get("/", response_model=List[Atendente])
def listar_atendentes(
    session: Session = Depends(get_session),
    nome: str | None = Query(None, description="Filtrar por nome parcial")
):
    query = select(Atendente)
    
    if nome:
        query = query.where(func.lower(Atendente.nome).contains(nome.lower()))
        
    return session.exec(query).all()

# --- READ (Por ID) ---
@router.get("/{atendente_id}", response_model=Atendente)
def obter_atendente(atendente_id: int, session: Session = Depends(get_session)):
    atendente = session.get(Atendente, atendente_id)
    if not atendente:
        raise HTTPException(status_code=404, detail="Atendente não encontrado")
    return atendente

# --- UPDATE ---
@router.patch("/{atendente_id}", response_model=Atendente)
def atualizar_atendente(atendente_id: int, atendente_data: AtendenteBase, session: Session = Depends(get_session)):
    db_atendente = session.get(Atendente, atendente_id)
    if not db_atendente:
        raise HTTPException(status_code=404, detail="Atendente não encontrado")
    
    dados = atendente_data.model_dump(exclude_unset=True)
    for key, value in dados.items():
        setattr(db_atendente, key, value)

    session.add(db_atendente)
    session.commit()
    session.refresh(db_atendente)
    return db_atendente

# --- DELETE ---
@router.delete("/{atendente_id}")
def deletar_atendente(atendente_id: int, session: Session = Depends(get_session)):
    db_atendente = session.get(Atendente, atendente_id)
    if not db_atendente:
        raise HTTPException(status_code=404, detail="Atendente não encontrado")
    
    session.delete(db_atendente)
    session.commit()
    return {"message": "Atendente removido com sucesso"}