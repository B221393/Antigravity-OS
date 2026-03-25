import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const LINE_API_BASE = "https://api.line.me/v2/bot";

type ToolResult = {
  content: Array<{ type: "text"; text: string }>;
  structuredContent?: unknown;
  isError?: boolean;
};

function getAccessToken(): string {
  const token = process.env.LINE_CHANNEL_ACCESS_TOKEN;
  if (!token) {
    throw new Error(
      "LINE_CHANNEL_ACCESS_TOKEN is not set. Set it in your environment before starting the server."
    );
  }
  return token;
}

async function lineApiRequest<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();
  const response = await fetch(`${LINE_API_BASE}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    const bodyText = await response.text();
    throw new Error(
      `LINE API request failed (${response.status} ${response.statusText}): ${bodyText}`
    );
  }

  if (response.status === 204) {
    return {} as T;
  }

  return (await response.json()) as T;
}

const server = new McpServer({
  name: "line-mcp-server",
  version: "1.0.0",
});

server.registerTool(
  "line_health_check",
  {
    title: "LINE health check",
    description:
      "Check whether LINE access token is configured and server can call LINE API.",
    inputSchema: {},
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true,
    },
  },
  async (): Promise<ToolResult> => {
    try {
      const hasToken = Boolean(process.env.LINE_CHANNEL_ACCESS_TOKEN);
      if (!hasToken) {
        return {
          isError: true,
          content: [
            {
              type: "text",
              text: "LINE_CHANNEL_ACCESS_TOKEN is not set.",
            },
          ],
          structuredContent: {
            ok: false,
            has_token: false,
          },
        };
      }

      const result = await lineApiRequest<{ userId: string }>(
        "/info",
        { method: "GET" }
      );

      return {
        content: [
          {
            type: "text",
            text: `LINE connection OK. botUserId=${result.userId}`,
          },
        ],
        structuredContent: {
          ok: true,
          has_token: true,
          bot_user_id: result.userId,
        },
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        isError: true,
        content: [{ type: "text", text: `Health check failed: ${message}` }],
        structuredContent: {
          ok: false,
          error: message,
        },
      };
    }
  }
);

server.registerTool(
  "line_push_message",
  {
    title: "Push LINE message",
    description:
      "Send a text message to a LINE user/group/room by ID using the push API.",
    inputSchema: {
      to: z
        .string()
        .min(1)
        .describe("LINE recipient ID (userId, groupId, or roomId)."),
      message: z.string().min(1).max(5000).describe("Text message to send."),
    },
    annotations: {
      readOnlyHint: false,
      destructiveHint: false,
      idempotentHint: false,
      openWorldHint: true,
    },
  },
  async ({ to, message }): Promise<ToolResult> => {
    try {
      await lineApiRequest("/message/push", {
        method: "POST",
        body: JSON.stringify({
          to,
          messages: [{ type: "text", text: message }],
        }),
      });

      const output = {
        ok: true,
        to,
        sent_message: message,
      };

      return {
        content: [
          {
            type: "text",
            text: `Message sent to ${to}`,
          },
        ],
        structuredContent: output,
      };
    } catch (error) {
      const messageText =
        error instanceof Error ? error.message : String(error);
      return {
        isError: true,
        content: [{ type: "text", text: `Failed to send message: ${messageText}` }],
        structuredContent: {
          ok: false,
          to,
          error: messageText,
        },
      };
    }
  }
);

server.registerTool(
  "line_get_profile",
  {
    title: "Get LINE user profile",
    description: "Get LINE user profile from userId.",
    inputSchema: {
      user_id: z.string().min(1).describe("Target LINE userId."),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true,
    },
  },
  async ({ user_id }): Promise<ToolResult> => {
    try {
      const profile = await lineApiRequest<{
        userId: string;
        displayName: string;
        pictureUrl?: string;
        statusMessage?: string;
      }>(`/profile/${encodeURIComponent(user_id)}`, { method: "GET" });

      const output = {
        user_id: profile.userId,
        display_name: profile.displayName,
        picture_url: profile.pictureUrl ?? null,
        status_message: profile.statusMessage ?? null,
      };

      return {
        content: [
          {
            type: "text",
            text: `Profile: ${output.display_name} (${output.user_id})`,
          },
        ],
        structuredContent: output,
      };
    } catch (error) {
      const message =
        error instanceof Error ? error.message : String(error);
      return {
        isError: true,
        content: [{ type: "text", text: `Failed to get profile: ${message}` }],
        structuredContent: {
          ok: false,
          user_id,
          error: message,
        },
      };
    }
  }
);

async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  process.stderr.write(`Failed to start LINE MCP server: ${message}\n`);
  process.exit(1);
});
