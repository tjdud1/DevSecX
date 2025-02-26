const express = require('express');
const axios = require('axios'); // LLM API 호출
const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());

// 코드 취약점 분석 엔드포인트
app.post('/analyze', async (req, res) => {
  const { code } = req.body;

  try {
    const llmResponse = await axios.post('https://api.groq.com/analyze', {
      code: code,
    });

    res.json({ result: llmResponse.data });
  } catch (error) {
    res.status(500).json({ error: 'LLM 분석 실패' });
  }
});

app.listen(PORT, () => {
  console.log(`서버 실행: http://localhost:${PORT}`);
});
