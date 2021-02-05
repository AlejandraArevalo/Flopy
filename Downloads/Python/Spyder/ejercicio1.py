#Este tutorial demuestra el uso de FloPy para desarrollar un modelo simple MODFLOW 6.
import os
import numpy as np
import matplotlib.pyplot as plt
import flopy
#datos
name = "ejercicio1"
h1 = 100
h2 = 90
Nlay = 10
N = 101
L = 400.0
H = 50.0
k = 1.0

#Crear los objetos del modelo Flopy
sim = flopy.mf6.MFSimulation(
    sim_name=name, exe_name="C:/Users/angie/Downloads/Python/mf6.2.0/bin/mf6", version="mf6", sim_ws="Workspace"
)
#Crear los objetos del modelo Flopy TDIS
tdis = flopy.mf6.ModflowTdis(
    sim, pname="tdis", time_units="DAYS", nper=1, perioddata=[(1.0, 1, 1.0)]
)

#Crear el objeto Flopy IMS Package
ims = flopy.mf6.ModflowIms(sim, pname="ims", complexity="SIMPLE")

#Cree el objeto de modelo Flopy groundwater flow (gwf)
model_nam_file = "{}.nam".format(name)
gwf = flopy.mf6.ModflowGwf(sim, modelname=name, model_nam_file=model_nam_file)

#Cree el paquete de discretización (DIS)
bot = np.linspace(-H / Nlay, -H, Nlay)
delrow = delcol = L / (N - 1)
dis = flopy.mf6.ModflowGwfdis(
    gwf,
    nlay=Nlay,
    nrow=N,
    ncol=N,
    delr=delrow,
    delc=delcol,
    top=0.0,
    botm=bot,
)

#Crear el paquete de condiciones iniciales (IC)
start = h1 * np.ones((Nlay, N, N))
ic = flopy.mf6.ModflowGwfic(gwf, pname="ic", strt=start)

#Cree el paquete de flujo de propiedades de nodo (NPF)
k=np.ones([10,N,N])
k[1,:,:]=5e-1
npf = flopy.mf6.ModflowGwfnpf(gwf, icelltype=1, k=k, save_flows=True, save_specific_discharge = True)

#Cree el paquete de cabeza constante (CHD)
chd_rec = []
chd_rec.append(((0, int(N / 4), int(N / 4)), h2))
chd_rec.append(((1, int(3*N / 4), int(3*N / 4)), h2-5))
for layer in range(0, Nlay):
    for row_col in range(0, N):
        chd_rec.append(((layer, row_col, 0), h1))
        chd_rec.append(((layer, row_col, N - 1), h1))
        if row_col != 0 and row_col != N - 1:
            chd_rec.append(((layer, 0, row_col), h1))
            chd_rec.append(((layer, N - 1, row_col), h1))
chd = flopy.mf6.ModflowGwfchd(
    gwf,
    maxbound=len(chd_rec),
    stress_period_data=chd_rec,
    save_flows=True,
)


iper = 0
ra = chd.stress_period_data.get_data(key=iper)
ra

# Create the output control (`OC`) Package impresion
headfile = "{}.hds".format(name)
head_filerecord = [headfile]
budgetfile = "{}.cbb".format(name)
budget_filerecord = [budgetfile]
saverecord = [("HEAD", "ALL"), ("BUDGET", "ALL")]
printrecord = [("HEAD", "LAST")]
oc = flopy.mf6.ModflowGwfoc(
    gwf,
    saverecord=saverecord,
    head_filerecord=head_filerecord,
    budget_filerecord=budget_filerecord,
    printrecord=printrecord,
)

#Cree los archivos de entrada modFLOW 6 y ejecute el modelo
sim.write_simulation()

#Ejecute la simulación
success, buff = sim.run_simulation()
if not success:
    raise Exception("MODFLOW 6 did not terminate normally.")
    
    
#Resultados del head posterior al proceso
#Graficar un mapa de la capa 1
headfile='Workspace' +'/'+headfile
hds = flopy.utils.binaryfile.HeadFile(headfile)
h = hds.get_data(kstpkper=(0, 0))
x = y = np.linspace(0, L, N)
y = y[::-1]
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
c = ax.contour(x, y, h[0], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%2.1f")

#Graficar un mapa de la capa 10
x = y = np.linspace(0, L, N)
y = y[::-1]
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
c = ax.contour(x, y, h[-1], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%1.1f")

#Trazar una sección transversal a lo largo de la fila 51
z = np.linspace(-H / Nlay / 2, -H + H / Nlay / 2, Nlay)
fig = plt.figure(figsize=(5, 2.5))
ax = fig.add_subplot(1, 1, 1, aspect="auto")
c = ax.contour(x, z, h[:, 50, :], np.arange(90, 100.1, 0.2), colors="black")
plt.clabel(c, fmt="%1.1f")

#Trazar un mapa de las capas 1 y 10
ibd = np.ones((Nlay, N, N), dtype=np.int)
for k, i, j in ra["cellid"]:
    ibd[k, i, j] = -1
    
fig, axes = plt.subplots(2, 1, figsize=(6, 12), constrained_layout=True)
# first subplot
ax = axes[0]
ax.set_title("Model Layer 1")
modelmap = flopy.plot.PlotMapView(model=gwf, ax=ax)
quadmesh = modelmap.plot_ibound(ibound=ibd)
linecollection = modelmap.plot_grid(lw=0.5, color="0.6")
contours = modelmap.contour_array(
    h[0], levels=np.arange(90, 100.1, 0.2), colors="green"
)
ax.clabel(contours, fmt="%2.1f")
# second subplot
ax = axes[1]
ax.set_title("Model Layer {}".format(Nlay))
modelmap = flopy.plot.PlotMapView(model=gwf, ax=ax, layer=Nlay - 1)
quadmesh = modelmap.plot_ibound(ibound=ibd)
linecollection = modelmap.plot_grid(lw=0.5, color="0.5")
pa = modelmap.plot_array(h[0])
contours = modelmap.contour_array(
    h[0], levels=np.arange(90, 100.1, 0.2), colors="black"
)
cb = plt.colorbar(pa, shrink=0.5, ax=ax)
ax.clabel(contours, fmt="%2.1f")
