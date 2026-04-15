
preguntas a convertir en query

¿Cuántas filas totales hay en la tabla ventas?

    SELECT COUNT(*) FROM ventas;

¿Cuántos países distintos (Country) hay?

    SELECT DISTINCT Country FROM ventas;

¿Cuál es el precio medio (UnitPrice) de los productos?

    SELECT SUM(UnitPrice * Quantity) / SUM(Quantity) AS precio_medio_ponderado FROM ventas WHERE Quantity > 0 AND UnitPrice > 0;

¿Cuáles son los 10 productos (Description) más vendidos por cantidad total (Quantity)?
    
    SELECT StockCode, Description, SUM(Quantity) AS total_vendido FROM ventas WHERE Quantity > 0 GROUP BY StockCode, Description  ORDER BY total_vendido DESC LIMIT 10;

¿Qué países generan más ingresos totales? (ingresos = Quantity * UnitPrice)
    
    SELECT Country,     SUM(Quantity * UnitPrice) AS ingresos_totales FROM ventas WHERE Quantity > 0 AND UnitPrice > 0 GROUP BY Country ORDER BY ingresos_totales DESC LIMIT 10; 

¿Cuántos clientes únicos (CustomerID) hay?

    SELECT COUNT(DISTINCT CustomerID) AS clientes_unicos FROM ventas;
