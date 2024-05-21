��    )      d  ;   �      �  1   �  -   �     �  &     G   3     {     �  8   �     �       2        Q     k  /   �  <   �  1   �  A   %  ^   g  �  �  /  ^  �   �  �  l  {  �  �  z  j     q   �  [   �  W   X  �   �  d   H  c   �      �   $  q   �  m      e   �  h   �  j   ]  >  �  y    �   �  4   y   2   �      �   (   �   9   !!     [!     y!  =   �!  %   �!     �!  :   "  '   Q"     y"  .   �"  >   �"  :   #  9   A#  o   {#  (  �#  �  *  �   �+  �  �,    >.  /  F0  �   v2  o   3  �   s3  {   �3  �   u4  c   $5  n   �5  2  �5  �   *7  k   �7  �   F8     �8  n   Q9  q   �9  L  2:  �  >                )       (   
                    $                                                "                                          &      	   '                           %   !   #                     
***** sub-Object Directory (all have .help()):

 A fill between two separate axes EXPERIMENTAL A number in pixels A plotly fill description EXPERIMENTAL Can be a single color value or list of color values from colour package Can be log or linear Color of the fill EXPERIMENTAL If true, will force show the item even if it has no data If true, will not show the item Possible theme keys:
 Sets the default min and max x value for this item Specifies the range units Unrecognized unit type: %s You must supply `mnemonic` or `name` (not both) `depth` and `data` have different lengths. data/depth: %d/%d `depth` cannot be `None`, you must supply a depth `mnemonic` and `name` are the same thing, please specify only one class Axis: part of a coordinate system and contains various pozo.Trace (and other drawables)
 class Trace: contains one drawable data array

Trace is a unit-aware pointer for a data and depth array. It also stores a mnemonic (name). It is not supposed to store data, but point to the data and then render that data into a graph later using the depth as the Y-axis. Depth and data must be the same shape at all times, they can be replaced together.

Data and its unit are versioned properties. That is, if you want to change the data without losing the original, you can use the functions as they are described below (new_version() etc). You can set the version with `mytrace.version =`. The depth and its unit are expected to be constants.

Pozo attempts to be agnostic towards array type: series, nparrays, polars, pandas, lists are all accepted. pint.Quantity wrappers are often accepted as well.

***** Constructor: pozo.Trace(...)
Args:
    data (array): most types of arrays are accepted, including one wrapped in pint.Quantity
    **kwargs:
        mnemonic (str): REQUIRED: the name/mnemonic of the trace
        name (str): synonym for mnemonic, don't include both
        unit (str or pint.Unit): describes the data unit
        depth (array): another array that must be the same size as data, can also be pint.Quantity
        depth_unit (str or pint.Unit): describes the depth unit
        original_data (any): A pointer to where the original data was extracted from, useful if planning to re-output to a LAS file
 method convert_depth_unit: will convert the depth to the specified unit, example ft to meters

Since we cannot graph traces specified with different depth units, this can be used to make a permanent conversion.

It will also change the recorded unit.

Args:
    unit (str or pint.Unit): the target unit
 method convert_unit: a convenience function to change the unit of your data

Most Trace functions don't permanently change and/or create new data arrays: this one does.

Args:
    unit (str or pint.Unit): the target unit
 method find_nearest: retrieve index and actual value of depth closes to input

If you're looking for a value at 1000ft, but we only have a value at 998 ft and 1001 ft, will return 1001 ft and its index

Args:
    value (number): The depth value you are looking for
Returns:
    idx (number): The index of the value closest to what you're looking for
    value (number): The actual value at that index
 method get_data: returns the data
Args:
    slice_by_depth (tuple): accepts a tuple using slice syntax (:) of positive values to select by depth
    force_unit (boolean): will force wrap the return in a pint.Quantity if True (default False)
    clean (boolean): a hack to deal with poorly behaved renderers, will remove all non-finite values (default False)
Returns:
    the data method get_depth: returns the depth array
Args:
    slice_by_depth (tuple): accepts a tuple using slice syntax (:) of positive values to select by depth
    force_unit (boolean): will force wrap the return in a pint.Quantity if True (default False)
    clean (boolean): a hack to deal with poorly behaved renderers, will remove depths where non-finite values in the data (default False)
Returns:
    depth array or slice method get_depth_unit: gets the unit associated with the depth
Returns:
    the unit exactly as it was set method get_dict: return relevant properties of trace as key-value dictionary

Returns:
    A key-value dictionary method get_mnemonic: get name/mnemonic of trace
Returns:
    The name/mnemonic of the trace method get_name: get name/mnemonic of trace
Returns:
    The name/mnemonic of the trace method get_theme: return the stored theme with a context object

Returns:
    A theme object (pozo.themes.help()) with attached context for this trace. method get_theme: returns a context-less theme definition

Returns:
    A theme, no context attached method get_unit: gets the unit associated with the data
Returns:
    the unit exactly as it was set method set_data: set the data and optionally the unit, depth, and depth_unit
Args:
    data (array): the data to set
    unit (str of pint.Unit): the unit associated with the data
    depth (array): an array of depth values
    depth_unit: the unit associated with the depth method set_depth: sets the depth
Args:
    depth (array): The depth to set
    depth_unit (str or pint.Unit): The depth's associated unit method set_depth_unit: sets the unit associated with the depth
Args:
    unit (str or pint.Unit): the unit to set method set_mnemonic: set name/mnemonic of trace
Args:
    mnemonic (str): The name/mnemonic you'd like to set method set_name: set name/mnemonic of trace
Args:
    name (str): The name/mnemonic you'd like to set method set_theme: sets the theme of object

Args:
    theme (Theme or dict): The theme you'd like to set method set_unit: sets the unit associated with the data
Args:
    unit (str or pint.Unit): the unit to set package pozo: the visualization engine, pozo

Para cambiar a español: `pozo.es()`

https://github.com/geopozo/pozo-demo is a good learning template and quickstart.

***** Description:

pozo creates a tree structure to describe your graph:

───Graph─┬─Track───Axis─┬─Trace: "CALI"
         │              └─Trace: "CGR"
         ├─Track─┬─Axis─┬─Trace: "RHOB"
         │       │      ├─Trace: "NPHI"
         │       │      ├─Trace: "LLD"
         │       │      └─Trace: "LLS"
         │       └─Axis───Trace: "ARP"
         └─Track───Axis───Trace: "RPA"

***** Highlighted sub-Objects:

    Main Objects:
                pozo.Graph              - The main object.
                pozo.Trace              - What stores data point and line data.

    Highlighted Items:
                pozo.themes.cangrejo    - A basic theme to jump-start styling. e.g. `myGraph.set_theme("cangrejo")`
                pozo.units.check_las()  - Print basic data analysis and sanitizing on your las files.
 package theme: a theme engine for pozo

    The theme package provides several theme objects, which can be attached to pozo graphs, tracks, axes, and traces (.set_theme()) to provide information about styling during rendering. Regular dictionaries can be theme objects, and their possible keys are described here. Other theme objects are described in their own documentation.

 Project-Id-Version: 
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2024-05-21 18:44-0400
Last-Translator: 
Language-Team: 
Language: es
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 3.4.2
 
***** sub-Objeto Directorio (todo tiene .help()):

 Un relleno entres dos ejes diferentes EXPERIMENTAL Un número en píxeles Un relleno de estilo plotly EXPERIMENTAL Se puede un color o lista de colores del paquete "colour" Se puede ser "log" o "linear" Color del relleno EXPERIMENTAL Si "True", hará la unidad visible, incluso si no tiene datos Si "True", no hará la unidad visible Claves de tema posibles:
 Se pone el mínimo y el máximo del valor para esta unidad Se ponen las unidades del rango "range" Tipo de unidad desconocido: %s Se debe dar o `mnemonic`o `name`, y no los dos `depth` y `data` tienen tamaños diferentes. data/depth: %d/%d `depth` no se puede ser `None`, debe haber una profundidad `menmonic` y `name` son los mismos: se especifca solo uno clase Axis (eje): parte de un sistema de coordinadas y contiene varios objetos pozo.Trace (y otros dibujables)
 clase Trace (trazo): contiene una tabla de datos dibujable

Trace es consciente de unidades, y una referencia a una tabla de datos y profundidades. Tambien se guarda una mnemotécnica, o nombre. No se debe almacenar datos, pero hacer referencia los datos y luego renderizar al gráfico usando la profundad como el eje Y. La profunidad y los datos deben tener el mismo tamaño a todo momento, y se pueden reemplazar al mismo tiemo.

Los datos y sus unidades son propriedades versionados. Es decir, si se quiere cambiar los datos sin perder los originales, se puede usar las funciones como se describen abajo (new_version(), etc). Se puede fijar la versión con el atributo `.version`, parte del trace. La profunidad y sus unidades deben ser constantes.

Pozo intenta ser agnóstico hacia el tipo de tabla: series, nparrays, polar, pandas, llists están bien. Tambien, contenendores de pint.Quanty están bien.

***** Constructor: pozo.Trace(...)
Args:
    data (table): Se aceptan tipos comunes, también en contenedor de pint.Quantity
    **kwargs:
        mnemonic (str): OBLIGATORIO: el nombre/mnemotécnica del trazo
        name (str):  sinónimo de mnemotécnica, no incluir los dos
        unit (str or pint.Unit): se describe la unidad de los datos
        depth (table): otra table, el mismo tamaño de data, que también puede ser un pint.Quantity
        depth_unit (str or pint.Unit): se describe la unidad de la profundiad
        original_data (cualquier): Una referencia a donde estuvieron los datos originales, que es útil si se genera un archivo de LAS nuevo
 método convert_depth_unit (convierte_unidad_de_profunidad): se convierte la table de profunidad a la unidad dada, por ejemplo ft a metros

Debido que no podemos renderizar trazos dados donde las profunidades tienen unidades distintas, esto puede hacer un cambio permanente

También, se cambia la unidad registrada y devuelte con get_depth_unit().

Args:
    unit (str o pint.Unit): la unidad querida
 método convert_unit (convierte_unidad): una función ayudable para cambiar la unidad de los datos

Si bien la mayoria de funciones de Trace no cambian ni crean datos nuevos, esto sí.

Args:

    unit (str o pint.Unit): la unidad querida
 método find_nearest (buscar más cerca): conseguir índice y valor de la profundidad más cerca de la buscada


Si se busca un valor a 1000 pies, pero solo hay valor entre 998 pies y 1001 pies, se devuelve el índice y valor de 1000 pies.

Args:
    value (número): La profundida que se busca
Returns:
    idx (número): El índice del valor más cerca de lo que se busca
    value (número): El valor actual al índice
 método get_data (saca_datos): devuelve los datos
Args:
     slice_by_depth (tuple): se accepta un tuple que se usa la misma sintaxis de un `slice` de python, pero solo se aceptan valores positivos de las profundidas buscadas
    force_unit (booleano): se hace que el valor devuelto siempre esta envueleto por un pint.Quantity (Falso predeterminado)
    clean (booleano): un hackeo para lidear con mal comportamiento de los renderizadores- se quitan los valores no-finitos (Falso predeterminado)
Devuelve:
    los datos método get_depth (saca_profundidad): devuelve la tabla de profunidad
Args:
    slice_by_depth (tuple): se accepta un tuple que se usa la misma sintaxis de un `slice` de python, pero solo se aceptan valores positivos de las profundidas buscadas
    force_unit (booleano): se hace que el valor devuelto siempre esta envueleto por un pint.Quantity (Falso predeterminado)
    clean (booleano): un hackeo para lidear con mal comportamiento de los renderizadores- se quitan los valores no-finitos en la tabla de datos (Falso predeterminado)
Devuelve:
    los datos método get_depth_unit (saca_unidad_de_profunidad): se consigue la unidad de la tabla de profundidades
Devuelve:
    la unidad como se pusó método get_dict: devuelve propriedades del trazo como diccionario de clave-valor

Devuelve:
    Un diccionario método get_mnemonic (saca_mnemotécnica): conseguir el nombre/mnemotécnica del trazo
Devuelve:
    El nombre/mnemotecnica del trazo método get_name (saca_nombre): conseguir el nombre/mnemotécnica del trazo
Devuelve:
    El nombre/mnemotécnica del trazo método get_theme (saca_tema): devuelve el tema guardado con un objeto do contexto

Devuelve:
    Un objeto de tema (pozo.themes.help()) con contexto adjunto para este trazo. método get_theme (saca_tema): se duevlve un tema sin contexto

Devuelve:
    Un tema, sin contexto método get_unit (saca_unidad): devuelve la unidad de los datos:
Devuelve:
    la unidad precisa como se fijó método set_data (pon_datos): poner los datos y talvez la unidad, profundidad, y la unidad de profundidad.
Args:
    data (tabla): los datos para poner
    unit (str o pint.Unit): la unidad de los datos
    depth (table): una tabla de los valores de profunidad
    depth_unit: la unidad de las profunidades método set_depth (pon_profundidad): poner la tabla de la profundidad
Args:
    depth (tabla): La table para poner
    depth_unit (str o pint.Unit): La unidad de la profunidad método set_depth_unit (pon_unidad_de_profunidad):
Args:
    unidad (str o pint.Unit): la unidad para poner método set_mnemonic (pon_mnemotécnica): poner nombre/mnemotécnica del trazo
Args:
    menomic (str): El nombre/mnemotécnica para poner método set_name (pon_nombre): fijar el nombre/mnemotécnica del trazo
Args:
    name (str): El nombre/mnemotécnica para poner método set_theme (pon_tema): se pone el tema del objeto

Args:
    theme (Theme o dict): El tema para ponerse método set_unit (pon_unidad): poner la unidad de los datos
Args:
    unit (str o pint.Unit): la unidad par poner paquete pozo: el motor de visualización

To change the english: `pozo.en()`

https://github.com/geopozo/pozo-demo-es es una buena plantilla.

***** Descripción:

pozo crea una estructura de árbol para describir el gráfico:

───Graph─┬─Track───Axis─┬─Trace: "CALI"
         │              └─Trace: "CGR"
         ├─Track─┬─Axis─┬─Trace: "RHOB"
         │       │      ├─Trace: "NPHI"
         │       │      ├─Trace: "LLD"
         │       │      └─Trace: "LLS"
         │       └─Axis───Trace: "ARP"
         └─Track───Axis───Trace: "RPA"

***** sub-Objetos Destacados:

    Objetos Principales:
                pozo.Graph              - El gráfico.
                pozo.Trace              - Lo que guarda los puntos y lineas (los datos).

    Unidades Destacadas:
                pozo.themes.cangrejo    - Un tema principal para empezar con un estilo. `myGraph.set_theme("cangrejo")`
                pozo.units.check_las()  - Imprimir un análisis basico para ayudar a lavar los archivos de las.
 paquete theme (tema): un motor de tema

    El paquete "theme" provee varios objetos de tema, lo que se pueden adjuntar a pozo.Graph, pozo.Track, pozo.Axis, y pozo.trace (`.set_theme()`) para proveer información del estilo sobre la renderización. Dicionarrios sencillos se pueden usar como objetos de tema, y sus claves posibles se describen acá. Otras opciones de objetos de tema se describen en su propio .help().

 