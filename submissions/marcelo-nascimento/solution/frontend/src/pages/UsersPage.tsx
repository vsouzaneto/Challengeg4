import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { EmptyState, ErrorState, LoadingState } from "../components/Common.js";
import { useAuth } from "../context/AuthContext.js";
import { api } from "../lib/api.js";
import { formatDate } from "../lib/format.js";
import type { ApplicationUser } from "../types.js";

type DialogMode = "create" | "edit" | "password";

interface DialogProps {
  mode: DialogMode;
  user: ApplicationUser | null;
  onClose: () => void;
  onSaved: () => Promise<void>;
}

function UserDialog({ mode, user, onClose, onSaved }: DialogProps) {
  const [name, setName] = useState(user?.name ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [password, setPassword] = useState("");
  const [isActive, setIsActive] = useState(user?.isActive ?? true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const { user: currentUser, logout, refreshSession } = useAuth();
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
    return () => dialog?.close();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      if (mode === "create") {
        await api.createUser({ name, email, password });
      } else if (mode === "edit" && user) {
        await api.updateUser(user.id, { name, email, isActive });
      } else if (mode === "password" && user) {
        await api.resetPassword(user.id, password);
      }
      if (mode === "password" && user?.id === currentUser?.id) {
        await logout();
      } else {
        await onSaved();
        if (mode === "edit" && user?.id === currentUser?.id) {
          await refreshSession();
        }
      }
      onClose();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Não foi possível salvar.");
    } finally {
      setSaving(false);
    }
  }

  const title = mode === "create" ? "Criar usuário" : mode === "edit" ? "Editar usuário" : "Redefinir senha";

  return (
    <dialog ref={dialogRef} className="user-dialog" aria-labelledby="user-dialog-title" onCancel={(event) => {
      event.preventDefault();
      onClose();
    }} onMouseDown={(event) => {
      if (event.target === event.currentTarget) {
        onClose();
      }
    }}>
      <div className="modal-dialog">
        <form className="modal-content" onSubmit={(event) => void handleSubmit(event)}>
          <div className="modal-header">
            <div><span className="eyebrow">Gestão de acesso</span><h2 className="modal-title" id="user-dialog-title">{title}</h2></div>
            <button className="icon-button" type="button" onClick={onClose} aria-label="Fechar"><i className="fa-solid fa-xmark" aria-hidden="true" /></button>
          </div>
          <div className="modal-body">
            {error ? <div className="alert alert-danger" role="alert">{error}</div> : null}
            {mode !== "password" ? (
              <>
                <label htmlFor="user-name">Nome<input id="user-name" value={name} onChange={(event) => setName(event.target.value)} minLength={2} maxLength={120} required autoFocus /></label>
                <label htmlFor="user-email">E-mail<input id="user-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} maxLength={256} required autoFocus={mode === "edit"} /></label>
              </>
            ) : null}
            {mode === "create" || mode === "password" ? (
              <label htmlFor="user-password">{mode === "create" ? "Senha inicial" : "Nova senha"}<input id="user-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} maxLength={200} required autoFocus={mode === "password"} /></label>
            ) : null}
            {mode === "edit" ? <label className="status-switch"><input type="checkbox" checked={isActive} onChange={(event) => setIsActive(event.target.checked)} disabled={user?.id === currentUser?.id} /><span><strong>Usuário ativo</strong><small>{user?.id === currentUser?.id ? "Você não pode desativar a própria conta." : "Usuários inativos não conseguem autenticar."}</small></span></label> : null}
            {mode === "create" ? <div className="info-banner compact"><i className="fa-solid fa-circle-info" aria-hidden="true" /><span>Todos os usuários pertencem à mesma classe e não possuem roles.</span></div> : null}
          </div>
          <div className="modal-footer">
            <button className="btn btn-outline-secondary" type="button" onClick={onClose}>Cancelar</button>
            <button className="btn btn-primary" type="submit" disabled={saving}>{saving ? <><span className="spinner-border spinner-border-sm" aria-hidden="true" /> Salvando...</> : "Salvar"}</button>
          </div>
        </form>
      </div>
    </dialog>
  );
}

export default function UsersPage() {
  const [users, setUsers] = useState<ApplicationUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dialog, setDialog] = useState<DialogMode | null>(null);
  const [selected, setSelected] = useState<ApplicationUser | null>(null);
  const [actionError, setActionError] = useState("");
  const [pendingUserId, setPendingUserId] = useState<number | null>(null);
  const requestVersion = useRef(0);
  const { user: currentUser } = useAuth();

  const load = useCallback(async () => {
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    try {
      const result = await api.users();
      if (version === requestVersion.current) {
        setUsers(result.data);
      }
    } catch (requestError) {
      if (version === requestVersion.current) {
        setError(requestError instanceof Error ? requestError.message : "Falha ao carregar os usuários.");
      }
    } finally {
      if (version === requestVersion.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void load();
    return () => {
      requestVersion.current += 1;
    };
  }, [load]);

  function openDialog(mode: DialogMode, user: ApplicationUser | null = null): void {
    setSelected(user);
    setDialog(mode);
  }

  async function toggleActive(user: ApplicationUser): Promise<void> {
    setActionError("");
    setPendingUserId(user.id);
    try {
      await api.updateUser(user.id, { name: user.name, email: user.email, isActive: !user.isActive });
      await load();
    } catch (requestError) {
      setActionError(requestError instanceof Error ? requestError.message : "Não foi possível alterar o status.");
    } finally {
      setPendingUserId(null);
    }
  }

  return (
    <div className="page-stack">
      <section className="panel">
        <div className="panel-heading">
          <div><span className="eyebrow">Acesso</span><h2>Usuários da aplicação</h2><p>{users.length} usuário{users.length === 1 ? "" : "s"} cadastrado{users.length === 1 ? "" : "s"}</p></div>
          <button className="btn btn-primary" type="button" onClick={() => openDialog("create")}><i className="fa-solid fa-user-plus" aria-hidden="true" /> Novo usuário</button>
        </div>
        {actionError ? <ErrorState message={actionError} /> : null}
        {loading ? <LoadingState label="Carregando usuários..." /> : null}
        {error ? <ErrorState message={error} onRetry={() => void load()} /> : null}
        {!loading && !error ? (
          users.length === 0 ? <EmptyState title="Nenhum usuário" message="Crie o primeiro usuário da aplicação." /> : (
            <div className="table-responsive">
              <table className="table users-table">
                <thead><tr><th>Nome</th><th>E-mail</th><th>Status</th><th>Criado em</th><th>Ações</th></tr></thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td data-label="Nome"><div className="user-cell"><span className="user-avatar small">{user.name.charAt(0).toUpperCase()}</span><strong>{user.name}</strong></div></td>
                      <td data-label="E-mail">{user.email}</td>
                      <td data-label="Status"><span className={`user-status ${user.isActive ? "active" : "inactive"}`}><i className={`fa-solid ${user.isActive ? "fa-circle-check" : "fa-circle-pause"}`} aria-hidden="true" /> {user.isActive ? "Ativo" : "Inativo"}</span></td>
                      <td data-label="Criado em">{formatDate(user.createdAt.slice(0, 10))}</td>
                      <td data-label="Ações"><div className="table-actions">
                        <button className="icon-button" type="button" title="Editar" aria-label={`Editar ${user.name}`} onClick={() => openDialog("edit", user)} disabled={pendingUserId !== null}><i className="fa-solid fa-pen" aria-hidden="true" /></button>
                        <button className="icon-button" type="button" title="Redefinir senha" aria-label={`Redefinir senha de ${user.name}`} onClick={() => openDialog("password", user)} disabled={pendingUserId !== null}><i className="fa-solid fa-key" aria-hidden="true" /></button>
                        <button className={`icon-button ${user.isActive ? "danger" : "success"}`} type="button" title={user.isActive ? "Desativar" : "Ativar"} aria-label={`${user.isActive ? "Desativar" : "Ativar"} ${user.name}`} onClick={() => void toggleActive(user)} disabled={pendingUserId !== null || user.id === currentUser?.id} aria-busy={pendingUserId === user.id}>{pendingUserId === user.id ? <span className="spinner-border spinner-border-sm" aria-hidden="true" /> : <i className={`fa-solid ${user.isActive ? "fa-user-slash" : "fa-user-check"}`} aria-hidden="true" />}</button>
                      </div></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : null}
      </section>
      {dialog ? <UserDialog key={`${dialog}-${selected?.id ?? "new"}`} mode={dialog} user={selected} onClose={() => setDialog(null)} onSaved={load} /> : null}
    </div>
  );
}
