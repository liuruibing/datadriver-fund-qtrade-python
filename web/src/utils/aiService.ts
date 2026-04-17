import axios from 'axios';

// AI API配置接口
interface AIConfig {
  openai?: {
    apiKey: string;
    baseURL?: string;
  };
  claude?: {
    apiKey: string;
    baseURL?: string;
  };
  qwen?: {
    apiKey: string;
    baseURL?: string;
  };
  ernie?: {
    apiKey: string;
    secretKey: string;
    baseURL?: string;
  };
}

// AI分析请求参数
interface AIAnalysisRequest {
  stockCode: string;
  stockName: string;
  aiModel: string;
  analysisType?: string;
}

// AI分析响应结果
interface AIAnalysisResult {
  overallRating: number;
  technicalRating: number;
  fundamentalRating: number;
  sentimentRating: number;
  investmentAdvice: string;
  technicalAnalysis: string;
  fundamentalAnalysis: string;
  riskWarning: string;
}

// 从环境变量获取配置
const getAIConfig = (): AIConfig => {
  return {
    openai: {
      apiKey: import.meta.env.VITE_OPENAI_API_KEY || '',
      baseURL: import.meta.env.VITE_OPENAI_BASE_URL || 'https://api.openai.com/v1'
    },
    claude: {
      apiKey: import.meta.env.VITE_CLAUDE_API_KEY || '',
      baseURL: import.meta.env.VITE_CLAUDE_BASE_URL || 'https://api.anthropic.com/v1'
    },
    qwen: {
      apiKey: import.meta.env.VITE_QWEN_API_KEY || '',
      baseURL: import.meta.env.VITE_QWEN_BASE_URL || 'https://dashscope.aliyuncs.com/api/v1'
    },
    ernie: {
      apiKey: import.meta.env.VITE_ERNIE_API_KEY || '',
      secretKey: import.meta.env.VITE_ERNIE_SECRET_KEY || '',
      baseURL: import.meta.env.VITE_ERNIE_BASE_URL || 'https://aip.baidubce.com'
    }
  };
};

// OpenAI GPT分析
const analyzeWithOpenAI = async (params: AIAnalysisRequest): Promise<AIAnalysisResult> => {
  const config = getAIConfig();
  if (!config.openai?.apiKey) {
    throw new Error('OpenAI API密钥未配置');
  }

  const prompt = `请对股票${params.stockName}(${params.stockCode})进行全面的技术分析和基本面分析，提供投资建议和风险提示。

请以JSON格式返回以下结构：
{
  "overallRating": 综合评分(0-5分),
  "technicalRating": 技术评分(0-5分),
  "fundamentalRating": 基本面评分(0-5分),
  "sentimentRating": 市场情绪评分(0-5分),
  "investmentAdvice": "投资建议(详细说明)",
  "technicalAnalysis": "技术分析(详细说明)",
  "fundamentalAnalysis": "基本面分析(详细说明)",
  "riskWarning": "风险提示(详细说明)"
}

请基于当前市场数据和分析方法进行专业分析。`;

  const response = await axios.post(
    `${config.openai.baseURL}/chat/completions`,
    {
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      max_tokens: 2000
    },
    {
      headers: {
        'Authorization': `Bearer ${config.openai.apiKey}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000
    }
  );

  const content = response.data.choices[0].message.content;
  const result = JSON.parse(content);

  return {
    overallRating: Math.min(5, Math.max(0, result.overallRating || 3.5)),
    technicalRating: Math.min(5, Math.max(0, result.technicalRating || 3.5)),
    fundamentalRating: Math.min(5, Math.max(0, result.fundamentalRating || 3.5)),
    sentimentRating: Math.min(5, Math.max(0, result.sentimentRating || 3.5)),
    investmentAdvice: result.investmentAdvice || '暂无投资建议',
    technicalAnalysis: result.technicalAnalysis || '暂无技术分析',
    fundamentalAnalysis: result.fundamentalAnalysis || '暂无基本面分析',
    riskWarning: result.riskWarning || '请注意投资风险'
  };
};

// Claude分析
const analyzeWithClaude = async (params: AIAnalysisRequest): Promise<AIAnalysisResult> => {
  const config = getAIConfig();
  if (!config.claude?.apiKey) {
    throw new Error('Claude API密钥未配置');
  }

  const prompt = `请对股票${params.stockName}(${params.stockCode})进行全面的技术分析和基本面分析，提供投资建议和风险提示。

请以JSON格式返回以下结构：
{
  "overallRating": 综合评分(0-5分),
  "technicalRating": 技术评分(0-5分),
  "fundamentalRating": 基本面评分(0-5分),
  "sentimentRating": 市场情绪评分(0-5分),
  "investmentAdvice": "投资建议(详细说明)",
  "technicalAnalysis": "技术分析(详细说明)",
  "fundamentalAnalysis": "基本面分析(详细说明)",
  "riskWarning": "风险提示(详细说明)"
}`;

  const response = await axios.post(
    `${config.claude.baseURL}/messages`,
    {
      model: 'claude-3-sonnet-20240229',
      max_tokens: 2000,
      messages: [{ role: 'user', content: prompt }]
    },
    {
      headers: {
        'x-api-key': config.claude.apiKey,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
      },
      timeout: 30000
    }
  );

  const content = response.data.content[0].text;
  const result = JSON.parse(content);

  return {
    overallRating: Math.min(5, Math.max(0, result.overallRating || 3.8)),
    technicalRating: Math.min(5, Math.max(0, result.technicalRating || 4.0)),
    fundamentalRating: Math.min(5, Math.max(0, result.fundamentalRating || 3.5)),
    sentimentRating: Math.min(5, Math.max(0, result.sentimentRating || 4.0)),
    investmentAdvice: result.investmentAdvice || '暂无投资建议',
    technicalAnalysis: result.technicalAnalysis || '暂无技术分析',
    fundamentalAnalysis: result.fundamentalAnalysis || '暂无基本面分析',
    riskWarning: result.riskWarning || '请注意投资风险'
  };
};

// 通义千问分析
const analyzeWithQwen = async (params: AIAnalysisRequest): Promise<AIAnalysisResult> => {
  const config = getAIConfig();
  if (!config.qwen?.apiKey) {
    throw new Error('通义千问API密钥未配置');
  }

  const prompt = `请对股票${params.stockName}(${params.stockCode})进行全面的技术分析和基本面分析，提供投资建议和风险提示。

请以JSON格式返回以下结构：
{
  "overallRating": 综合评分(0-5分),
  "technicalRating": 技术评分(0-5分),
  "fundamentalRating": 基本面评分(0-5分),
  "sentimentRating": 市场情绪评分(0-5分),
  "investmentAdvice": "投资建议(详细说明)",
  "technicalAnalysis": "技术分析(详细说明)",
  "fundamentalAnalysis": "基本面分析(详细说明)",
  "riskWarning": "风险提示(详细说明)"
}`;

  const response = await axios.post(
    `${config.qwen.baseURL}/services/aigc/text-generation/generation`,
    {
      model: 'qwen-turbo',
      input: {
        messages: [{ role: 'user', content: prompt }]
      },
      parameters: {
        temperature: 0.7,
        max_tokens: 2000
      }
    },
    {
      headers: {
        'Authorization': `Bearer ${config.qwen.apiKey}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000
    }
  );

  const content = response.data.output.text;
  const result = JSON.parse(content);

  return {
    overallRating: Math.min(5, Math.max(0, result.overallRating || 4.0)),
    technicalRating: Math.min(5, Math.max(0, result.technicalRating || 4.1)),
    fundamentalRating: Math.min(5, Math.max(0, result.fundamentalRating || 3.9)),
    sentimentRating: Math.min(5, Math.max(0, result.sentimentRating || 4.2)),
    investmentAdvice: result.investmentAdvice || '暂无投资建议',
    technicalAnalysis: result.technicalAnalysis || '暂无技术分析',
    fundamentalAnalysis: result.fundamentalAnalysis || '暂无基本面分析',
    riskWarning: result.riskWarning || '请注意投资风险'
  };
};

// 文心一言分析
const analyzeWithErnie = async (params: AIAnalysisRequest): Promise<AIAnalysisResult> => {
  const config = getAIConfig();
  if (!config.ernie?.apiKey || !config.ernie?.secretKey) {
    throw new Error('文心一言API密钥未配置');
  }

  // 先获取access_token
  const tokenResponse = await axios.post(
    `${config.ernie.baseURL}/oauth/2.0/token`,
    null,
    {
      params: {
        grant_type: 'client_credentials',
        client_id: config.ernie.apiKey,
        client_secret: config.ernie.secretKey
      }
    }
  );

  const accessToken = tokenResponse.data.access_token;

  const prompt = `请对股票${params.stockName}(${params.stockCode})进行全面的技术分析和基本面分析，提供投资建议和风险提示。

请以JSON格式返回以下结构：
{
  "overallRating": 综合评分(0-5分),
  "technicalRating": 技术评分(0-5分),
  "fundamentalRating": 基本面评分(0-5分),
  "sentimentRating": 市场情绪评分(0-5分),
  "investmentAdvice": "投资建议(详细说明)",
  "technicalAnalysis": "技术分析(详细说明)",
  "fundamentalAnalysis": "基本面分析(详细说明)",
  "riskWarning": "风险提示(详细说明)"
}`;

  const response = await axios.post(
    `${config.ernie.baseURL}/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions`,
    {
      model: 'ernie-4.0',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      max_tokens: 2000
    },
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000
    }
  );

  const content = response.data.result;
  const result = JSON.parse(content);

  return {
    overallRating: Math.min(5, Math.max(0, result.overallRating || 3.8)),
    technicalRating: Math.min(5, Math.max(0, result.technicalRating || 4.0)),
    fundamentalRating: Math.min(5, Math.max(0, result.fundamentalRating || 3.5)),
    sentimentRating: Math.min(5, Math.max(0, result.sentimentRating || 4.0)),
    investmentAdvice: result.investmentAdvice || '暂无投资建议',
    technicalAnalysis: result.technicalAnalysis || '暂无技术分析',
    fundamentalAnalysis: result.fundamentalAnalysis || '暂无基本面分析',
    riskWarning: result.riskWarning || '请注意投资风险'
  };
};

// 主分析函数
export const aiStockAnalysis = async (params: AIAnalysisRequest): Promise<AIAnalysisResult> => {
  try {
    switch (params.aiModel.toLowerCase()) {
      case 'gpt4':
      case 'gpt-4':
        return await analyzeWithOpenAI(params);
      case 'gpt35':
      case 'gpt-3.5':
        // GPT-3.5使用相同的API，只是模型名不同
        return await analyzeWithOpenAI({ ...params, aiModel: 'gpt-3.5-turbo' });
      case 'claude':
        return await analyzeWithClaude(params);
      case 'qwen':
        return await analyzeWithQwen(params);
      case 'ernie':
        return await analyzeWithErnie(params);
      default:
        throw new Error(`不支持的AI模型: ${params.aiModel}`);
    }
  } catch (error: any) {
    console.error('AI API调用失败:', error);

    // 提供更友好的错误信息
    let errorMessage = 'AI分析服务暂时不可用';
    if (error.message?.includes('API密钥未配置')) {
      errorMessage = 'AI服务未配置，请联系管理员配置API密钥';
    } else if (error.message?.includes('timeout')) {
      errorMessage = 'AI服务响应超时，请稍后重试';
    } else if (error.response?.status === 429) {
      errorMessage = 'AI服务请求过于频繁，请稍后重试';
    } else if (error.response?.status === 401) {
      errorMessage = 'AI服务认证失败，请检查API密钥配置';
    } else if (error.response?.status >= 500) {
      errorMessage = 'AI服务暂时不可用，请稍后重试';
    }

    const enhancedError = new Error(errorMessage);
    (enhancedError as any).originalError = error;
    throw enhancedError;
  }
};

// 获取支持的AI模型列表
export const getSupportedAIModels = () => {
  const config = getAIConfig();
  const models = [];

  if (config.openai?.apiKey) {
    models.push({ value: 'gpt4', label: 'GPT-4' });
    models.push({ value: 'gpt35', label: 'GPT-3.5' });
  }
  if (config.claude?.apiKey) {
    models.push({ value: 'claude', label: 'Claude' });
  }
  if (config.qwen?.apiKey) {
    models.push({ value: 'qwen', label: '通义千问' });
  }
  if (config.ernie?.apiKey && config.ernie?.secretKey) {
    models.push({ value: 'ernie', label: '文心一言' });
  }

  return models;
};
