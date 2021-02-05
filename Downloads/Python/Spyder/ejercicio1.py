
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
""" 
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

#condicionn de draneje en la primer capa 
drn_datos = []
for column in range(51):
        drn_datos.append(((0, 51, column), 78.5+0.2*column, 0.3))
drn= flopy.mf6.ModflowGwfdrn(gwf,
                             stress_period_data=drn_datos
)

#condicionn de draneje en la primer capa 
drn_datos = []
for column in range(51):
        drn_datos.append(((0, 51, column), 78.5+0.2*column, 0.3))
drn= flopy.mf6.ModflowGwfdrn(gwf,
                             stress_period_data=drn_datos
)

#condicionn de draneje en la primer capa 
drn_datos = []
for column in range(51):
        drn_datos.append(((0, 51, column), 78.5+0.2*column, 0.3))
drn= flopy.mf6.ModflowGwfdrn(gwf,
                             stress_period_data=drn_datos
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


#prueba de grafico de flechas a la de dios
cbc_file = os.path.join('Workspace', "ejercicio1.cbb")
cbc = flopy.utils.CellBudgetFile(cbc_file, precision='double')
spdis = cbc.get_data(text="SPDIS")

head_file = os.path.join('Workspace', "ejercicio1.hds")
head = flopy.utils.HeadFile(head_file)
hdata = head.get_alldata()[0]

fig = plt.figure(figsize=(8, 8))

mapview = flopy.plot.PlotMapView(model=gwf, layer=0)
linecollection = mapview.plot_grid()
quadmesh = mapview.plot_array(a=hdata, alpha=0.5, masked_values=[1e30])
quiver = mapview.plot_specific_discharge(spdis[0])
#inactive = mapview.plot_inactive()

plt.title("Specific Discharge (" + r'$L/T$' + ')')
plt.colorbar(quadmesh, shrink=0.75);