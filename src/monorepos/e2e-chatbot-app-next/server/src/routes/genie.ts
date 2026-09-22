import {
  Router,
  type Request,
  type Response,
  type Router as RouterType,
} from 'express';
import { askGenie, publicRooms, resolveRoomSpace } from '../lib/genie-client';

export const genieRouter: RouterType = Router();

genieRouter.get('/rooms', (_req: Request, res: Response) => {
  res.json({ rooms: publicRooms() });
});

genieRouter.post('/:alias/messages', async (req: Request, res: Response) => {
  try {
    resolveRoomSpace(req.params.alias);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown room';
    const status = message.includes('not configured') ? 503 : 404;
    return res.status(status).json({ error: message });
  }

  const content =
    typeof req.body?.content === 'string' ? req.body.content : '';
  const conversationId =
    typeof req.body?.conversationId === 'string'
      ? req.body.conversationId
      : undefined;

  if (!content.trim()) {
    return res.status(400).json({ error: 'content is required' });
  }

  try {
    const reply = await askGenie({
      alias: req.params.alias,
      content,
      conversationId,
    });
    return res.json(reply);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Genie failed';
    return res.status(502).json({ error: message });
  }
});
