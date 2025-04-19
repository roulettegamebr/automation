import tkinter as tk
import subprocess
import threading
import time
import random
import uiautomator2 as u2

ADB_PATH = "adb"
ciclos_ativos = {}
stop_flags = {}
ciclos_contador = {}

def run_adb(device, *args):
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run([ADB_PATH, "-s", device, "shell"] + list(args),
                                capture_output=True, text=True, startupinfo=startupinfo)
        return result.stdout.strip()
    except Exception as e:
        return f"Erro: {str(e)}"

def log(widget, message):
    timestamp = time.strftime("[%H:%M:%S] ")
    widget.config(state=tk.NORMAL)
    widget.insert(tk.END, timestamp + message + "\n")
    widget.see(tk.END)
    widget.config(state=tk.DISABLED)
    print(timestamp + message)

def obter_item_anuncio(d):
    try:
        adviews = d.xpath("//*[contains(@resource-id, 'adView') and .//*[@clickable='true']]").all()
        return random.choice(adviews) if adviews else None
    except Exception as e:
        print(f"[ERRO] XPath falhou: {e}")
        return None

def aceitar_termos_navegador(d, device_id, text_widget):
    try:
        for res_id in ["mark.via.gp:id/ed", "mark.via.gp:id/ee"]:
            button = d(resourceId=res_id)
            if button.exists(timeout=3):
                x, y = button.center()
                d.click(x, y)
                log(text_widget, f"{device_id}: Botão 'Agree' ({res_id}) clicado em ({x},{y})")
                time.sleep(5)  # Espera após o clique no Agree

        continuar = d(text="Continue loading")
        if continuar.exists(timeout=5):
            x, y = continuar.center()
            d.click(x, y)
            log(text_widget, f"{device_id}: Botão 'Continue loading' clicado em ({x},{y})")
            time.sleep(2)

        episodio = d(text="Continue to next episode")
        if episodio.exists(timeout=5):
            x, y = episodio.center()
            d.click(x, y)
            log(text_widget, f"{device_id}: Botão 'Continue to next episode' clicado em ({x},{y})")
            time.sleep(5)

    except Exception as e:
        log(text_widget, f"{device_id}: Erro ao aceitar termos: {e}")

def limpar_rastreadores(device_id, text_widget):
    paths = [
        "/data/system/usagestats",
        "/data/system/dropbox",
        "/data/log"
    ]
    for path in paths:
        run_adb(device_id, "su", "-c", f"rm -rf {path}")
        log(text_widget, f"{device_id}: Limpando {path}")

def run_automation_loop(device_id, text_widget, label_ciclos):
    d = u2.connect_usb(device_id)
    ciclos_ativos[device_id] = True
    stop_flags[device_id] = False
    ciclos_contador[device_id] = 0

    while not stop_flags[device_id]:
        try:
            ciclos_contador[device_id] += 1
            ciclo_n = ciclos_contador[device_id]
            label_ciclos.config(text=f"Ciclos: {ciclo_n}")
            log(text_widget, f"🚀 {device_id}: Iniciando ciclo {ciclo_n}")

            limpar_rastreadores(device_id, text_widget)

            if ciclo_n % redefinir_id_var.get() == 0:
                run_adb(device_id, "pm", "clear", "mark.via.gp")
                log(text_widget, f"{device_id}: Dados do Via Browser limpos.")

            for pkg in ["com.android.browser", "mark.via.gp", "com.google.android.gms"]:
                run_adb(device_id, "am", "force-stop", pkg)

            run_adb(device_id, "pm", "clear", "com.google.android.gms")
            log(text_widget, f"{device_id}: Dados do GMS (ID de publicidade) limpos.")

            run_adb(device_id, "pm", "clear", "com.android.vending")
            log(text_widget, f"{device_id}: Dados da Play Store limpos.")

            run_adb(device_id, "pm", "clear", package_name_var.get())
            log(text_widget, f"{device_id}: Dados do app {package_name_var.get()} limpos.")

            run_adb(device_id, "input", "keyevent", "4")
            run_adb(device_id, "am", "start", "-n", f"{package_name_var.get()}/.MainActivity")
            log(text_widget, f"{device_id}: App iniciado.")

            time.sleep(random.uniform(espera_min_var.get(), espera_max_var.get()))

            for _ in range(10):
                if "MainActivity" in run_adb(device_id, "dumpsys", "activity", "activities"):
                    break
                log(text_widget, f"{device_id}: Aguardando aba principal do app...")
                time.sleep(2)

            timeout_redirecionamento = random.uniform(timeout_min_var.get(), timeout_max_var.get())
            fim = time.time() + timeout_redirecionamento
            redirecionado = False

            while time.time() < fim:
                anuncio = obter_item_anuncio(d)
                if anuncio:
                    x, y = anuncio.center()
                    d.click(x, y)
                    log(text_widget, f"{device_id}: Anúncio clicado em ({x},{y})")
                    time.sleep(5)
                    current = run_adb(device_id, "dumpsys", "activity", "activities")
                    if any(pkg in current for pkg in ["com.android.browser", "mark.via.gp", "com.android.vending"]):
                        redirecionado = True
                        if "mark.via.gp" in current:
                            aceitar_termos_navegador(d, device_id, text_widget)
                        break
                else:
                    time.sleep(2)

            if not redirecionado:
                log(text_widget, f"⚠️ {device_id}: Nenhum redirecionamento detectado.")
                continue

            time.sleep(random.uniform(carregar_min_var.get(), carregar_max_var.get()))
            fim_interacao = time.time() + random.randint(interacao_min_var.get(), interacao_max_var.get())

            nivel_rolagem = 5
            while time.time() < fim_interacao:
                direcao = random.choice(["cima", "baixo"])
                if direcao == "cima" and nivel_rolagem > 0:
                    y_start = 500
                    y_end = 1000
                    nivel_rolagem -= 1
                    log(text_widget, f"{device_id}: Rolando para CIMA (nível: {nivel_rolagem})")
                elif direcao == "baixo" and nivel_rolagem < 10:
                    y_start = 1000
                    y_end = 500
                    nivel_rolagem += 1
                    log(text_widget, f"{device_id}: Rolando para BAIXO (nível: {nivel_rolagem})")
                else:
                    log(text_widget, f"{device_id}: Limite de rolagem para {direcao.upper()} alcançado")
                    continue
                x = random.choice([300, 250, 350])
                run_adb(device_id, "input", "swipe", str(x), str(y_start), str(x), str(y_end))
                time.sleep(random.uniform(2, 4))

            run_adb(device_id, "am", "force-stop", package_name_var.get())
            time.sleep(2)
            log(text_widget, f"✅ {device_id}: Ciclo {ciclo_n} finalizado.")
        except Exception as e:
            log(text_widget, f"{device_id}: ERRO - {str(e)}")
            break

    ciclos_ativos[device_id] = False

def criar_variaveis_configuraveis():
    global espera_min_var, espera_max_var, timeout_min_var, timeout_max_var
    global carregar_min_var, carregar_max_var, interacao_min_var, interacao_max_var
    global redefinir_id_var, package_name_var
    espera_min_var = tk.IntVar(value=15)
    espera_max_var = tk.IntVar(value=20)
    timeout_min_var = tk.IntVar(value=20)
    timeout_max_var = tk.IntVar(value=40)
    carregar_min_var = tk.IntVar(value=10)
    carregar_max_var = tk.IntVar(value=15)
    interacao_min_var = tk.IntVar(value=15)
    interacao_max_var = tk.IntVar(value=100)
    redefinir_id_var = tk.IntVar(value=1)
    package_name_var = tk.StringVar(value="digite sua package aqui")

def criar_interface():
    global listbox
    root = tk.Tk()
    root.title("Automação ADB Estável")
    criar_variaveis_configuraveis()

    frame_cfg = tk.LabelFrame(root, text="Configurações", padx=10, pady=10)
    frame_cfg.pack(padx=10, pady=10)

    tk.Label(frame_cfg, text="Pacote do App:").grid(row=0, column=0)
    tk.Entry(frame_cfg, textvariable=package_name_var, width=30).grid(row=0, column=1, columnspan=2)

    labels = [
        ("Espera antes (s):", espera_min_var, espera_max_var),
        ("Timeout publicidade (s):", timeout_min_var, timeout_max_var),
        ("Tempo carregar página (s):", carregar_min_var, carregar_max_var),
        ("Interação (rolagem) (s):", interacao_min_var, interacao_max_var)
    ]

    for i, (label, var_min, var_max) in enumerate(labels, start=1):
        tk.Label(frame_cfg, text=label).grid(row=i, column=0)
        tk.Spinbox(frame_cfg, from_=1, to=100, textvariable=var_min, width=5).grid(row=i, column=1)
        tk.Spinbox(frame_cfg, from_=1, to=100, textvariable=var_max, width=5).grid(row=i, column=2)

    tk.Label(frame_cfg, text="Redefinir ID a cada (ciclos):").grid(row=5, column=0)
    tk.Spinbox(frame_cfg, from_=1, to=100, textvariable=redefinir_id_var, width=5).grid(row=5, column=1)

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)
    tk.Label(frame, text="Dispositivos disponíveis:").pack()
    listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, width=50, height=10)
    listbox.pack(pady=5)

    tk.Button(frame, text="🔄 Atualizar", command=atualizar_lista).pack(pady=5)
    tk.Button(frame, text="▶ Iniciar", command=iniciar_automacao).pack(pady=5)

    # Exibe versão do bot
    tk.Label(root, text="Bot V1.2", font=("Segoe UI", 9, "italic"), fg="gray").pack(pady=(0, 10))

    atualizar_lista()
    root.mainloop()

def atualizar_lista():
    listbox.delete(0, tk.END)
    for dev in get_devices():
        listbox.insert(tk.END, dev)

def iniciar_automacao():
    for i in listbox.curselection():
        dev = listbox.get(i)
        if not ciclos_ativos.get(dev):
            criar_janela_dispositivo(dev)

def criar_janela_dispositivo(device_id):
    janela = tk.Toplevel()
    janela.title(f"Dispositivo: {device_id}")
    tk.Label(janela, text=f"Automação - {device_id}", font=("Segoe UI", 10, "bold")).pack(pady=5)
    label_ciclos = tk.Label(janela, text="Ciclos: 0", font=("Segoe UI", 10))
    label_ciclos.pack()
    text_area = tk.Text(janela, height=20, width=60, state=tk.DISABLED)
    text_area.pack(padx=10, pady=5)
    tk.Button(janela, text="⛔ Parar", bg="red", fg="white",
              command=lambda: parar_automacao(device_id, text_area)).pack(pady=5)
    threading.Thread(target=run_automation_loop, args=(device_id, text_area, label_ciclos), daemon=True).start()

def parar_automacao(device_id, text_widget):
    stop_flags[device_id] = True
    log(text_widget, f"{device_id}: Parada solicitada.")

def get_devices():
    try:
        output = subprocess.check_output([ADB_PATH, "devices"], text=True).strip().split("\n")[1:]
        return [line.split("\t")[0] for line in output if "device" in line]
    except:
        return []

criar_interface()
