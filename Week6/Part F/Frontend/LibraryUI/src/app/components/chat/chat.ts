import { CommonModule } from '@angular/common';
import {
  Component,
  OnDestroy
} from '@angular/core';

import { FormsModule } from '@angular/forms';

import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class ChatComponent implements OnDestroy {

  question = '';
  answer = '';

  isStreaming = false;
  errorMessage = '';

  private abortController: AbortController | null = null;

  constructor(
    private chatService: ChatService
  ) {}

  async ask(): Promise<void> {

    const question = this.question.trim();

    if (!question) {
      return;
    }

    this.answer = '';
    this.errorMessage = '';
    this.isStreaming = true;

    this.abortController = new AbortController();

    try {

      await this.chatService.askStream(
        question,
        (chunk: string) => {
          this.answer += chunk;
        },
        this.abortController.signal
      );

    } catch (error: any) {

      if (error?.name === 'AbortError') {
        console.log('Stream cancelled.');
      } else {
        console.error(error);

        this.errorMessage =
          'Unable to stream the AI response.';
      }

    } finally {

      this.isStreaming = false;
      this.abortController = null;
    }
  }

  stopStreaming(): void {

    if (this.abortController) {
      this.abortController.abort();
    }
  }

  ngOnDestroy(): void {
    this.stopStreaming();
  }
}