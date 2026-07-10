from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.authController import AuthController
from app.api.v1.usersController import UsersController
from app.repositories.user_repository import UserRepository
from app.core.db_config import db_plugin
from app.core.security import jwt_auth
from app.core.exceptions import GLOBAL_EXCEPTION_HANDLERS


# ====================================================
# 🛡️ AUTOMATIZACIÓN NATIVA: CREACIÓN DEL ADMINISTRADOR
# ====================================================
async def create_default_admin(app: Litestar) -> None:
    print("\n🚀 [WardenClass Auth] Verificando existencia del Administrador por defecto...")
    try:
        from sqlalchemy import select
        from app.models.user import UserModel 
        from app.domain.structs import UserRole, UserCredentials
        # 🔥 IMPORTAMOS LA LOGICA OFICIAL DE TU CAPA DE SERVICIOS
        from app.services.user_service import register_new_user
        
        session_maker = None
        state_keys = ["db_session_maker", "session_maker", "sqlalchemy_sessionmaker"]
        for key in state_keys:
            if hasattr(app.state, key):
                session_maker = getattr(app.state, key)
                break
                
        if not session_maker and hasattr(app.state, "_state") and isinstance(app.state._state, dict):
            for k, v in app.state._state.items():
                if "session" in k.lower() or "maker" in k.lower():
                    session_maker = v
                    break

        if not session_maker and hasattr(db_plugin, "config"):
            session_maker = db_plugin.config.session_maker

        if not session_maker:
            raise Exception("No se pudo mapear el gestor de sesiones asíncronas desde Litestar.")

        admin_email = "admin@focus.cl"

        # 1. Verificamos si ya existe el usuario de forma limpia
        async with session_maker() as session:
            stmt = select(UserModel).where(UserModel.email == admin_email)
            result = await session.execute(stmt)
            admin_existe = result.scalar_one_or_none()
            
            if not admin_existe:
                print(f"➕ [Auth] No se encontró a {admin_email}. Invocando servicio nativo 'register_new_user'...")
                
                # 2. Instanciamos el repositorio usando la sesión asíncrona activa del loop
                user_repo = UserRepository(session=session)
                
                # 3. Estructuramos las credenciales usando tu clase oficial msgspec.Struct
                credentials = UserCredentials(
                    email=admin_email,
                    password="admin.",
                    role=UserRole.ADMINISTRADOR # Rol correcto de tu Enum
                )
                
                # 4. Llamamos a tu servicio nativo asíncrono para que haga el registro completo
                # Pasa por tu encriptador real y hace el session.add() por ti
                await register_new_user(data=credentials, user_repo=user_repo)
                
                # 5. Confirmamos los cambios en la base de datos de forma segura
                await session.commit()
                print("🛡️ [Auth] Administrador por defecto creado exitosamente mediante la capa de servicios.")
                print(f"🔑 Credenciales listas -> Email: {admin_email} | Password: admin. | Rol: {UserRole.ADMINISTRADOR.value}\n")
            else:
                print("✅ [Auth] El Administrador ya se encuentra materializado legítimamente en la Base de Datos.\n")
                
    except Exception as e:
        print(f"⚠️ [Auth - Error] No se pudo ejecutar la auto-creación nativa: {e}\n")
# ====================================================
# DEPENDENCIAS Y CONFIGURACIONES ORIGINALES (SIN TOCAR)
# ====================================================
async def provide_user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)

app = Litestar(
    route_handlers=[
        AuthController,
        UsersController
    ],
    on_app_init=[jwt_auth.on_app_init],
    # ⚡ HOOK DE ARRANQUE: Registra la función de verificación automática sin alterar el flujo del servidor
    on_startup=[create_default_admin], 
    plugins=[db_plugin],
    dependencies={
        "user_repo": Provide(provide_user_repo)
    },
    exception_handlers=GLOBAL_EXCEPTION_HANDLERS,
    debug=False
)