
import unittest

from calculadora_modular import calcular_modular


class TestCalculadoraModular(unittest.TestCase):

    def test_ejemplos_tarea(self):
        casos = [
            ("(7^3 + 4 * 5) * 2", 23, 13),
            ("((15 + 7) * 3 - 2^4) / 5", 29, 10),
            ("(3^4 * 2 + 7) / (11 - 5^2)", 31, 30),
            ("(8 * (13 + 5^2) - 3^3) / (2^4 + 1)", 37, 25),
            (
                "((6^2 * 3 + 7) / (2^3 - 5))"
                " * (11 + 4^3) - 9",
                41,
                37,
            ),
        ]

        for expresion, p, esperado in casos:
            with self.subTest(expresion=expresion):
                self.assertEqual(
                    calcular_modular(expresion, p),
                    esperado
                )

    def test_entradas_invalidas(self):
        casos = [
            ("", 23),
            ("   ", 23),
            ("hola + 3", 23),
            ("3 + @", 23),
            ("(3 + 5", 23),
            ("5 / 0", 23),
            ("5 / 23", 23),
            ("2.5 + 3", 23),
            ("3 // 2", 23),
            ("3 + 5", 12),
            ("3 + 5", 1),
        ]

        for expresion, p in casos:
            with self.subTest(expresion=expresion, p=p):
                with self.assertRaises(ValueError):
                    calcular_modular(expresion, p)

    def test_espacios(self):
        self.assertEqual(
            calcular_modular("  3 + 5  ", 23),
            8
        )

    def test_numeros_negativos(self):
        self.assertEqual(
            calcular_modular("-5 + 2", 23),
            20
        )

    def test_exponente_negativo(self):
        self.assertEqual(
            calcular_modular("2^(-1)", 23),
            12
        )


if __name__ == "__main__":
    unittest.main()
