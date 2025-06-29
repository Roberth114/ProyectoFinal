import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import seaborn as sns
import threading
import time
import hashlib

# ===============================
# AUTENTICACIÓN CON GOOGLE SHEETS
# ===============================
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(
    r'C:\Users\HP-18\Desktop\ProyectoFinal\inventario-zapateria-credenciales.json',
    scopes=scope
)
client = gspread.authorize(creds)
sheet = client.open("Inventario Zapatería").sheet1

# ====================
# LECTURA DE DATOS
# ====================
def cargar_datos():
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df["Marca_Modelo"] = df["Marca"] + " - " + df["Modelo"]
    df["ValorTotal"] = df["Cantidad"] * df["Precio"]
    valor_total_por_modelo = df.groupby("Marca_Modelo")["ValorTotal"].sum()
    cantidad_por_modelo = df.groupby("Marca_Modelo")["Cantidad"].sum()
    df["Marca_Modelo_Valor"] = df["Marca_Modelo"].apply(lambda mm: f"{mm} (${int(valor_total_por_modelo[mm]):,})")
    df["Marca_Modelo_Cantidad"] = df["Marca_Modelo"].apply(lambda mm: f"{mm} ({cantidad_por_modelo[mm]})")
    return df

# ====================
# ESTILO Y COLORES
# ====================
sns.set(style="whitegrid")
colors = sns.color_palette("tab20")
plot_index = [0]
last_hash = [None]
df = cargar_datos()

# ====================
# FUNCIONES DE GRÁFICAS
# ====================
def plot1(ax):
    sns.barplot(data=df, x="ValorTotal", y="Categoría", hue="Marca_Modelo_Valor", ax=ax, palette=colors, width=2, dodge=True)
    ax.set_title("Valor Total por Categoría (Marca - Modelo)")
    ax.set_xlabel("Valor Total (COP)")
    ax.set_ylabel("Categoría")
    ax.legend(title="Marca - Modelo", bbox_to_anchor=(1.05, 1), loc='upper left')

def plot2(ax):
    sns.barplot(data=df, x="Cantidad", y="Categoría", hue="Marca_Modelo_Cantidad", ax=ax, palette=colors, width=2, dodge=True)
    ax.set_title("Cantidad por Categoría (Marca - Modelo)")
    ax.set_xlabel("Cantidad")
    ax.set_ylabel("Categoría")
    ax.legend(title="Marca - Modelo", bbox_to_anchor=(1.05, 1), loc='upper left')

def plot3(ax):
    sns.barplot(data=df, x="Talla", y="Cantidad", hue="Marca_Modelo_Cantidad", ax=ax, palette=colors, width=2)
    ax.set_title("Cantidad por Talla y Modelo")
    ax.set_xlabel("Talla")
    ax.set_ylabel("Cantidad")
    ax.legend(title="Marca - Modelo", bbox_to_anchor=(1.05, 1), loc='upper left')

def plot4(ax):
    sns.barplot(data=df, x="Cantidad", y="Color", hue="Marca_Modelo_Cantidad", ax=ax, palette=colors, width=2)
    ax.set_title("Cantidad por Color y Modelo")
    ax.set_xlabel("Cantidad")
    ax.set_ylabel("Color")
    ax.legend(title="Marca - Modelo", bbox_to_anchor=(1.05, 1), loc='upper left')

plots = [plot1, plot2, plot3, plot4]

# ====================
# ACTUALIZAR PLOT
# ====================
def update_plot():
    global df
    ax.clear()
    plots[plot_index[0]](ax)
    plt.draw()

# ====================
# REFRESCO AUTOMÁTICO
# ====================
def get_df_hash(df):
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

def auto_refresh(interval=3):
    global df
    while True:
        time.sleep(interval)
        new_df = cargar_datos()
        new_hash = get_df_hash(new_df)
        if new_hash != last_hash[0]:
            df = new_df
            last_hash[0] = new_hash
            update_plot()

# ====================
# FUNCIONES DE BOTONES
# ====================
def next_plot(event):
    plot_index[0] = (plot_index[0] + 1) % len(plots)
    update_plot()

def prev_plot(event):
    plot_index[0] = (plot_index[0] - 1) % len(plots)
    update_plot()

def save_plot(event):
    filename = f"grafica_{plot_index[0]+1}.png"
    plt.savefig(filename)
    print(f"Gráfica guardada como {filename}")

# ====================
# VENTANA PRINCIPAL
# ====================
fig, ax = plt.subplots(figsize=(16, 9))
plt.subplots_adjust(left=0.1, right=0.7, bottom=0.25)
plots[plot_index[0]](ax)
last_hash[0] = get_df_hash(df)

# Botones
ax_save = plt.axes([0.7, 0.13, 0.21, 0.065])
ax_prev = plt.axes([0.7, 0.05, 0.1, 0.065])
ax_next = plt.axes([0.81, 0.05, 0.1, 0.065])

b_save = Button(ax_save, 'Guardar Gráfica')
b_save.on_clicked(save_plot)

b_prev = Button(ax_prev, 'Anterior')
b_prev.on_clicked(prev_plot)

b_next = Button(ax_next, 'Siguiente')
b_next.on_clicked(next_plot)

# Lanzar hilo de refresco
threading.Thread(target=lambda: auto_refresh(3), daemon=True).start()

plt.show()
#colgrapen2@gmail.com
