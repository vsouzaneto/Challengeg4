// Esquema exposto ao text-to-SQL. Tabelas de autenticação (users, sessions) ficam de fora por desenho.
export const SQL_SCHEMA = `
tickets(
  id TEXT, source TEXT -- 'dataset' (histórico Dataset 1) | 'portal' | 'demo'
  customer_name TEXT, channel TEXT -- 'Email','Chat','Phone','Social media'
  product TEXT, subject TEXT, topic TEXT -- assunto/intenção ('Account access','Refund request',...)
  created_at INTEGER -- epoch em MILISSEGUNDOS
  status TEXT -- 'new','open','pending','escalated','resolved','closed'
  assignee TEXT, category TEXT -- 8 categorias do classificador ('Hardware','Access',...)
  category_conf REAL, team TEXT, priority TEXT -- 'Low','Medium','High','Critical' (calculada pela IA)
  sentiment TEXT -- 'Positive','Neutral','Frustrated','Angry'
  sentiment_score INTEGER, ai_confidence REAL -- score 0..1 do gate
  decision TEXT -- 'auto','suggest','human'
  risk_level TEXT -- 'LOW','MEDIUM','HIGH'
  risk_reasons TEXT -- JSON array de strings
  csat INTEGER -- 1..5 ou NULL
  automated INTEGER -- 1 se a IA respondeu sozinha
  first_response_at INTEGER, resolved_at INTEGER -- epoch ms
  dataset_type TEXT, dataset_priority TEXT -- campos originais do Dataset 1
)
messages(id, ticket_id TEXT, role TEXT -- 'customer','ai','agent','system'
  , body TEXT, created_at INTEGER)
events(id, ticket_id TEXT, type TEXT -- 'escalated','returned_to_ai','reply_accepted','reply_edited','reply_rejected','knowledge_gap','csat','frustration_detected'
  , payload TEXT, created_at INTEGER)
kb_articles(id, title TEXT, topic TEXT, source TEXT, uses INTEGER, created_at INTEGER)
kb_gaps(id, question TEXT, topic TEXT, category TEXT, occurrences INTEGER, status TEXT -- 'pending','resolved','dismissed'
  , created_at INTEGER)
`;
