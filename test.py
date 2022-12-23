import unittest
import bot

class BotTest(unittest.TestCase):
  def test_get_news(self):
    obj = 'abc'
    kol = 5
    expect_res= []
    result = bot.get_news(obj, kol)
    self.assertEqual(expect_res, result)

  def test_content(self):
    with open(f'start.txt', 'r', encoding="utf8") as file:
      expect_res = file.read()
      file.close()

    filen = 'start'
    result = bot.content(filen)
    self.assertEqual(expect_res, result)



if __name__ == '__main__':
  unittest.main()