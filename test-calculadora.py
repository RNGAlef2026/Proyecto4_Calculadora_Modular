import importlib.util
import unittest
import tkinter as tk
from pathlib import Path

spec = importlib.util.spec_from_file_location('calculadora_modular', Path(__file__).with_name('calculadora_modular.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class Pruebas(unittest.TestCase):
    def test_ejemplos(self):
        expected = [13, 10, 30, 25, 37]
        for (expr,p),answer in zip(mod.EJEMPLOS.values(),expected):
            with self.subTest(expr=expr):
                self.assertEqual(mod.calcular_modular(expr,p),answer)
                value, steps = mod.calcular_con_procedimiento(expr,p)
                self.assertEqual(value,answer)
                self.assertTrue(len(steps)>2)

    def test_errores(self):
        for expr,p in [('',23),('   ',23),('3+@',23),('3 + hola',23),('(3+4',23),('5/0',23),('5/23',23),('2.5+3',23),('3//2',23),('3+5',12),('3+5',1),('2^(2^100)',23),('2^(-100001)',23)]:
            with self.subTest(expr=expr,p=p):
                with self.assertRaises(ValueError):
                    mod.calcular_modular(expr,p)

    def test_validos(self):
        for expr,p,expected in [(' 3 + 5 ',23,8),('-5+2',23,20),('2^(-1)',23,12),('7/5+3',23,9),('2^3^2',23,pow(2,9,23))]:
            with self.subTest(expr=expr):
                self.assertEqual(mod.calcular_modular(expr,p),expected)

    def test_gui(self):
        root=tk.Tk()
        root.withdraw()
        try:
            app=mod.CalculadoraModular(root)
            self.assertIsInstance(app.campo_pasos,tk.Text)
            for label in mod.EJEMPLOS:
                app.combo_ejemplos.set(label)
                app.cargar_ejemplo()
                app.calcular()
                self.assertNotEqual(app.resultado.get(),'ERROR')
                self.assertIn('RESULTADO FINAL',app.campo_pasos.get('1.0','end'))
            app.limpiar()
            self.assertEqual(app.campo_pasos.get('1.0','end').strip(),'')
            app.expresion.set('3+@')
            app.calcular()
            self.assertEqual(app.resultado.get(),'ERROR')
            self.assertEqual(app.campo_pasos.get('1.0','end').strip(),'')
        finally:
            root.destroy()

if __name__=='__main__':
    unittest.main(verbosity=2)
