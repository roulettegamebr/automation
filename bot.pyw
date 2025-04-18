import tkinter as tk
import subprocess
import threading
import time
import random
import math
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
                time.sleep(2)
                return True
        log(text_widget, f"{device_id}: Nenhum botão 'Agree' encontrado (IDs testados).")
    except Exception as e:
        log(text_widget, f"{device_id}: Erro ao procurar/clicar em 'Agree': {e}")
    return False

def run_automation_loop(device_id, text_widget, label_ciclos):
    d = u2.connect_usb(device_id)
    ciclos_ativos[device_id] = True
    stop_flags[device_id] = False
    ciclos_contador[device_id] = 0
    tempos_redirecionamento = []

    while not stop_flags[device_id]:
        try:
            ciclos_contador[device_id] += 1
            ciclo_n = ciclos_contador[device_id]
            label_ciclos.config(text=f"Ciclos: {ciclo_n}")
            log(text_widget, f"🚀 {device_id}: Iniciando ciclo {ciclo_n}")

            if ciclo_n % redefinir_id_var.get() == 0:
                log(text_widget, f"{device_id}: Limpando dados do Via Browser (ciclo {ciclo_n})...")
                run_adb(device_id, "pm", "clear", "mark.via.gp")
                time.sleep(1.5)

            inicio_ciclo = time.time()
            for pkg in ["com.android.browser", "mark.via.gp", "com.google.android.gms"]:
                run_adb(device_id, "am", "force-stop", pkg)
            time.sleep(2.6)

            log(text_widget, f"{device_id}: Limpando dados do GMS...")
            run_adb(device_id, "pm", "clear", "com.google.android.gms")
            time.sleep(1.5)

            log(text_widget, f"{device_id}: Limpando dados da Play Store...")
            run_adb(device_id, "pm", "clear", "com.android.vending")
            time.sleep(1.5)

            log(text_widget, f"{device_id}: Limpando dados do OneTap...")
            run_adb(device_id, "pm", "clear", "hang.man.word.guessing.games")
            time.sleep(1.5)
            run_adb(device_id, "input", "keyevent", "4")
            log(text_widget, f"{device_id}: Saiu do OneTap com botão voltar.")

            run_adb(device_id, "am", "start", "-n", "hang.man.word.guessing.games/.MainActivity")
            log(text_widget, f"{device_id}: OneTap iniciado.")
            tempo_inicio_onetap = time.time()
            espera_onetap = random.uniform(espera_min_var.get(), espera_max_var.get())
            log(text_widget, f"{device_id}: Aguardando {espera_onetap:.1f}s antes de procurar publicidade...")
            time.sleep(espera_onetap)

            timeout_redirecionamento = random.uniform(timeout_min_var.get(), timeout_max_var.get())
            fim = time.time() + timeout_redirecionamento
            redirecionado = False
            log(text_widget, f"{device_id}: Procurando publicidade (máx {timeout_redirecionamento:.1f}s)...")

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
                        log(text_widget, f"{device_id}: Redirecionamento detectado com sucesso.")
                        if "mark.via.gp" in current:
                            aceitar_termos_navegador(d, device_id, text_widget)
                        break
                else:
                    log(text_widget, f"{device_id}: Nenhum anúncio detectado, tentando novamente...")
                    time.sleep(2.5)

            tempo_redir = time.time() - tempo_inicio_onetap
            tempos_redirecionamento.append(tempo_redir)

            if not redirecionado:
                log(text_widget, f"⚠️ {device_id}: Publicidade não detectada após tempo limite.")
                continue

            log(text_widget, f"{device_id}: Publicidade detectada após {tempo_redir:.1f}s")

            tempo_carregamento = random.uniform(carregar_min_var.get(), carregar_max_var.get())
            log(text_widget, f"{device_id}: Aguardando {tempo_carregamento:.1f}s para carregamento da página...")
            time.sleep(tempo_carregamento)

            tempo_interacao = random.randint(interacao_min_var.get(), interacao_max_var.get())
            fim_interacao = time.time() + tempo_interacao
            log(text_widget, f"{device_id}: Iniciando rolagens (tempo total: ~{tempo_interacao}s)")

            while time.time() < fim_interacao:
                tipo_rolagem = random.choice(["vertical", "diagonal"])
                if tipo_rolagem == "vertical":
                    x = 300
                    y_start = random.randint(700, 1000)
                    y_end = random.randint(400, 700)
                    run_adb(device_id, "input", "swipe", str(x), str(y_start), str(x), str(y_end))
                    log(text_widget, f"{device_id}: Rolagem vertical ({x},{y_start}) → ({x},{y_end})")
                else:
                    x_start = random.choice([100, 200, 300])
                    y_start = random.randint(900, 1100)
                    x_end = x_start + random.randint(150, 250)
                    y_end = y_start - random.randint(300, 500)
                    run_adb(device_id, "input", "swipe", str(x_start), str(y_start), str(x_end), str(y_end))
                    log(text_widget, f"{device_id}: Rolagem diagonal ({x_start},{y_start}) → ({x_end},{y_end})")

                pausa = round(random.uniform(1.5, 3.5) * math.pi, 4)
                log(text_widget, f"{device_id}: Pausa de {pausa:.4f}s após rolagem")
                time.sleep(pausa)

            run_adb(device_id, "am", "force-stop", "hang.man.word.guessing.games")
            run_adb(device_id, "input", "keyevent", "4")
            time.sleep(random.uniform(1.5, 3.0))
            run_adb(device_id, "input", "keyevent", "4")

            for pkg in ["com.android.browser", "mark.via.gp", "com.google.android.gms"]:
                run_adb(device_id, "am", "force-stop", pkg)

            duracao = time.time() - inicio_ciclo
            log(text_widget, f"✅ {device_id}: Ciclo {ciclo_n} concluído em {duracao:.1f}s")
            time.sleep(2)

        except Exception as e:
            log(text_widget, f"{device_id}: ERRO - {str(e)}")
            break

    ciclos_ativos[device_id] = False

def criar_variaveis_configuraveis():
    global espera_min_var, espera_max_var, timeout_min_var, timeout_max_var
    global carregar_min_var, carregar_max_var, interacao_min_var, interacao_max_var, redefinir_id_var

    espera_min_var = tk.IntVar(value=8)
    espera_max_var = tk.IntVar(value=16)
    timeout_min_var = tk.IntVar(value=20)
    timeout_max_var = tk.IntVar(value=40)
    carregar_min_var = tk.IntVar(value=5)
    carregar_max_var = tk.IntVar(value=12)
    interacao_min_var = tk.IntVar(value=15)
    interacao_max_var = tk.IntVar(value=30)
    redefinir_id_var = tk.IntVar(value=2)

def criar_interface():
    global listbox
    root = tk.Tk()
    root.title("Automação ADB Estável")

    criar_variaveis_configuraveis()

    frame_cfg = tk.LabelFrame(root, text="Configurações de Tempo", padx=10, pady=10)
    frame_cfg.pack(padx=10, pady=10)

    tk.Label(frame_cfg, text="Espera antes (s):").grid(row=0, column=0)
    tk.Spinbox(frame_cfg, from_=1, to=60, textvariable=espera_min_var, width=5).grid(row=0, column=1)
    tk.Spinbox(frame_cfg, from_=1, to=60, textvariable=espera_max_var, width=5).grid(row=0, column=2)

    tk.Label(frame_cfg, text="Timeout publicidade (s):").grid(row=1, column=0)
    tk.Spinbox(frame_cfg, from_=1, to=60, textvariable=timeout_min_var, width=5).grid(row=1, column=1)
    tk.Spinbox(frame_cfg, from_=1, to=60, textvariable=timeout_max_var, width=5).grid(row=1, column=2)

    tk.Label(frame_cfg, text="Tempo carregar página (s):").grid(row=2, column=0)
    tk.Spinbox(frame_cfg, from_=1, to=30, textvariable=carregar_min_var, width=5).grid(row=2, column=1)
    tk.Spinbox(frame_cfg, from_=1, to=30, textvariable=carregar_max_var, width=5).grid(row=2, column=2)

    tk.Label(frame_cfg, text="Interação (rolagem) (s):").grid(row=3, column=0)
    tk.Spinbox(frame_cfg, from_=1, to=60, textvariable=interacao_min_var, width=5).grid(row=3, column=1)
    tk.Spinbox(frame_cfg, from_=1, to=60, textvariable=interacao_max_var, width=5).grid(row=3, column=2)

    tk.Label(frame_cfg, text="Redefinir ID a cada (ciclos):").grid(row=4, column=0)
    tk.Spinbox(frame_cfg, from_=1, to=100, textvariable=redefinir_id_var, width=5).grid(row=4, column=1)

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    tk.Label(frame, text="Dispositivos disponíveis:").pack()
    listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, width=50, height=10)
    listbox.pack(pady=5)

    tk.Button(frame, text="🔄 Atualizar", command=atualizar_lista).pack(pady=5)
    tk.Button(frame, text="▶ Iniciar", command=iniciar_automacao).pack(pady=5)

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
