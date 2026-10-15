import { Injectable } from '@angular/core';

export interface AgentEvent {
  event: string;
  data: any;
}

@Injectable({
  providedIn: 'root'
})
export class AgentRunService {

  private readonly baseUrl =
    'http://localhost:5194/api/assistant/agent/runs';


  private getToken(): string {
    return (
      localStorage.getItem('token') ||
      localStorage.getItem('jwt') ||
      localStorage.getItem('authToken') ||
      ''
    );
  }


  async startRun(
    message: string,
    onEvent: (event: AgentEvent) => void,
    signal?: AbortSignal
  ): Promise<void> {

    const response =
      await fetch(
        this.baseUrl,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',

            'Authorization':
              `Bearer ${this.getToken()}`
          },

          body: JSON.stringify({
            message
          }),

          signal
        }
      );


    if (response.status === 429) {
      throw new Error(
        'RATE_LIMIT'
      );
    }


    if (!response.ok) {
      throw new Error(
        `HTTP_${response.status}`
      );
    }


    await this.readSse(
      response,
      onEvent
    );
  }


  async resumeRun(
    threadId: string,
    approved: boolean,
    onEvent: (event: AgentEvent) => void
  ): Promise<void> {

    const response =
      await fetch(
        `${this.baseUrl}/${threadId}/resume`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',

            'Authorization':
              `Bearer ${this.getToken()}`
          },

          body: JSON.stringify({
            approved
          })
        }
      );


    if (response.status === 429) {
      throw new Error(
        'RATE_LIMIT'
      );
    }


    if (!response.ok) {
      throw new Error(
        `HTTP_${response.status}`
      );
    }


    await this.readSse(
      response,
      onEvent
    );
  }


  async getRun(
    threadId: string
  ): Promise<any> {

    const response =
      await fetch(
        `${this.baseUrl}/${threadId}`,
        {
          headers: {
            'Authorization':
              `Bearer ${this.getToken()}`
          }
        }
      );


    if (response.status === 404) {
      throw new Error(
        'RUN_NOT_FOUND'
      );
    }


    if (!response.ok) {
      throw new Error(
        `HTTP_${response.status}`
      );
    }


    return response.json();
  }


  async cancelRun(
    threadId: string
  ): Promise<any> {

    const response =
      await fetch(
        `${this.baseUrl}/${threadId}/cancel`,
        {
          method: 'POST',

          headers: {
            'Authorization':
              `Bearer ${this.getToken()}`
          }
        }
      );


    if (!response.ok) {
      throw new Error(
        `HTTP_${response.status}`
      );
    }


    return response.json();
  }


  private async readSse(
    response: Response,
    onEvent:
      (event: AgentEvent) => void
  ): Promise<void> {

    const reader =
      response.body!
        .getReader();

    const decoder =
      new TextDecoder();

    let buffer = '';


    while (true) {

      const {
        value,
        done
      } =
        await reader.read();


      if (done) {
        break;
      }


      buffer +=
        decoder.decode(
          value,
          {
            stream: true
          }
        );


      const blocks =
        buffer.split('\n\n');

      buffer =
        blocks.pop() || '';


      for (const block of blocks) {

        let eventName = '';
        let dataText = '';


        for (
          const line
          of block.split('\n')
        ) {

          if (
            line.startsWith(
              'event:'
            )
          ) {

            eventName =
              line.substring(6)
                .trim();
          }


          if (
            line.startsWith(
              'data:'
            )
          ) {

            dataText +=
              line.substring(5)
                .trim();
          }
        }


        if (
          eventName &&
          dataText
        ) {

          try {

            onEvent({
              event:
                eventName,

              data:
                JSON.parse(
                  dataText
                )
            });

          } catch {

            console.warn(
              'Invalid SSE data',
              dataText
            );
          }
        }
      }
    }
  }
}