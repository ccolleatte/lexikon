import { createServer } from 'http';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { Server } from './.svelte-kit/output/server/index.js';
import { manifest } from './.svelte-kit/output/server/manifest.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const server = new Server({ manifest });

await server.init({
	env: process.env
});

const httpServer = createServer(async (req, res) => {
	const request = new Request(`http://${req.headers.host}${req.url}`, {
		method: req.method,
		headers: new Headers(req.headers),
		body: req.method === 'GET' || req.method === 'HEAD' ? undefined : req
	});

	const response = await server.respond(request, {
		getClientAddress: () => req.socket.remoteAddress
	});

	res.writeHead(response.status, Object.fromEntries(response.headers));

	if (response.body) {
		res.end(await response.text());
	} else {
		res.end();
	}
});

const port = process.env.PORT || 3000;
const host = process.env.HOST || '0.0.0.0';

httpServer.listen(port, host, () => {
	console.log(`🚀 Server listening on http://${host}:${port}`);
});
