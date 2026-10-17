import { Injectable } from '@angular/core';

import { environment } from '../../environments/environment';
import { AuthService } from './auth';

@Injectable({
  providedIn: 'root'
})
export class ChatService {

  private readonly sessionKey =
    'library-ai-session-id';

  constructor(
    private auth: AuthService
  ) {}

  getSessionId(): string {

    let sessionId =
      localStorage.getItem(
        this.sessionKey
      );

    if (!sessionId) {

      if (
        typeof crypto !== 'undefined'
        && crypto.randomUUID
      ) {
        sessionId =
          crypto.randomUUID();
      } else {
        sessionId =
          `session-${Date.now()}`;
      }

      localStorage.setItem(
        this.sessionKey,
        sessionId
      );
    }

    return sessionId;
  }


  async askStream(
    question: string,
    onChunk: (text: string) => void,
    signal?: AbortSignal
  ): Promise<void> {

    const token =
      this.auth.getToken();

    const headers:
      Record<string, string> = {
        'Content-Type':
          'application/json'
      };

    if (token) {
      headers['Authorization'] =
        `Bearer ${token}`;
    }

    const response =
      await fetch(
        `${environment.apiUrl}/api/Assistant/ask/stream`,
        {
          method: 'POST',
          headers,
          body: JSON.stringify({
            question,
            sessionId:
              this.getSessionId()
          }),
          signal
        }
      );

    if (!response.ok) {

      if (response.status === 503) {
        throw new Error(
          'AI_TEMPORARILY_UNAVAILABLE'
        );
      }

      throw new Error(
        `Streaming request failed: ${response.status}`
      );
    }

    if (!response.body) {
      throw new Error(
        'Streaming response body was empty.'
      );
    }

    const reader =
      response.body.getReader();

    const decoder =
      new TextDecoder();

    let buffer = '';

    while (true) {

      const {
        done,
        value
      } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(
        value,
        {
          stream: true
        }
      );

      const events =
        buffer.split('\n\n');

      buffer =
        events.pop() ?? '';

      for (const event of events) {

        const lines =
          event.split('\n');

        for (const line of lines) {

          if (
            !line.startsWith('data:')
          ) {
            continue;
          }

          const text =
            line
              .substring(5)
              .trimStart();

          if (
            text === '[DONE]'
          ) {
            return;
          }

          onChunk(text);
        }
      }
    }
  }


  async clearSession():
    Promise<void> {

    const sessionId =
      this.getSessionId();

    await fetch(
      `${environment.apiUrl}/api/Assistant/session/clear`,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json'
        },
        body: JSON.stringify({
          sessionId
        })
      }
    );

    localStorage.removeItem(
      this.sessionKey
    );
  }
}