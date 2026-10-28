import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tickettriage.tickets import crear_ticket


class TestCrearTicket(unittest.TestCase):
    def test_crea_ticket_con_datos_limpios(self):
        t = crear_ticket("  Login caído ", "No puedo entrar", "acme")
        self.assertEqual(t.titulo, "Login caído")

    def test_titulo_vacio_falla(self):
        with self.assertRaises(ValueError):
            crear_ticket("   ", "x", "acme")


if __name__ == "__main__":
    unittest.main()
