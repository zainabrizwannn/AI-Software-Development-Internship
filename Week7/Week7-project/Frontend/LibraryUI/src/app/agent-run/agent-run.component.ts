import {
  Component,
  OnInit
} from '@angular/core';

import {
  CommonModule
} from '@angular/common';

import {
  FormsModule
} from '@angular/forms';

import {
  AgentEvent,
  AgentRunService
} from '../services/agent-run.service';


interface TimelineItem {
  type: string;
  title: string;
  text: string;
}


@Component({
  selector: 'app-agent-run',

  standalone: true,

  imports: [
    CommonModule,
    FormsModule
  ],

  templateUrl:
    './agent-run.component.html',

  styleUrls: [
    './agent-run.component.css'
  ]
})
export class AgentRunComponent
  implements OnInit {

  message = '';

  answer = '';

  threadId:
    string | null = null;

  status =
    'idle';

  loading =
    false;

  approvalLoading =
    false;

  pendingApproval:
    any = null;

  errorMessage =
    '';

  timeline:
    TimelineItem[] = [];

  private abortController:
    AbortController | null =
      null;


  constructor(
    private agentService:
      AgentRunService
  ) {}


  async ngOnInit() {

    const stored =
      localStorage.getItem(
        'activeAgentThreadId'
      );


    if (stored) {

      this.threadId =
        stored;

      await this.restoreRun();
    }
  }


  async start() {

    if (
      !this.message.trim()
    ) {
      return;
    }


    this.answer = '';
    this.timeline = [];
    this.errorMessage = '';
    this.pendingApproval = null;

    this.loading = true;
    this.status = 'running';

    this.abortController =
      new AbortController();


    try {

      await this.agentService
        .startRun(
          this.message,
          event =>
            this.handleEvent(
              event
            ),
          this.abortController.signal
        );

    } catch (error: any) {

      if (
        error?.name ===
        'AbortError'
      ) {

        this.status =
          'cancelled';

        return;
      }


      if (
        error?.message ===
        'RATE_LIMIT'
      ) {

        this.errorMessage =
          'Too many AI requests. Please wait a moment and try again.';

      } else {

        this.errorMessage =
          'The agent could not complete the request.';
      }

      this.status =
        'failed';

    } finally {

      this.loading =
        false;
    }
  }


  private handleEvent(
    event: AgentEvent
  ) {

    switch (
      event.event
    ) {

      case 'step':

        if (
          event.data.threadId
        ) {

          this.threadId =
            event.data.threadId;

          localStorage.setItem(
            'activeAgentThreadId',
            this.threadId!
          );
        }


        this.timeline.push({
          type:
            event.data.kind,

          title:
            event.data.name ||
            'Agent',

          text:
            event.data.summary ||
            ''
        });

        break;


      case 'token':

        this.answer +=
          event.data.text;

        break;


      case
        'approval_required':

        this.threadId =
          event.data.threadId;

        this.pendingApproval =
          event.data;

        this.status =
          'pending_approval';

        localStorage.setItem(
          'activeAgentThreadId',
          this.threadId!
        );

        break;


      case 'final':

        this.answer =
          event.data.answer;

        this.status =
          'completed';

        this.pendingApproval =
          null;

        localStorage.removeItem(
          'activeAgentThreadId'
        );

        break;


      case 'error':

        this.errorMessage =
          event.data.message;

        this.status =
          'failed';

        break;
    }
  }


  async approve(
    approved: boolean
  ) {

    if (
      !this.threadId ||
      this.approvalLoading
    ) {
      return;
    }


    this.approvalLoading =
      true;


    try {

      await this.agentService
        .resumeRun(
          this.threadId,
          approved,
          event =>
            this.handleEvent(
              event
            )
        );

    } catch {

      this.errorMessage =
        'Could not resume the agent run.';

    } finally {

      this.approvalLoading =
        false;
    }
  }


  async cancel() {

    if (!this.threadId) {
      return;
    }


    try {

      await this.agentService
        .cancelRun(
          this.threadId
        );

      this.abortController
        ?.abort();

      this.status =
        'cancelled';

      this.loading =
        false;

      this.pendingApproval =
        null;

      localStorage.removeItem(
        'activeAgentThreadId'
      );

    } catch {

      this.errorMessage =
        'Could not cancel the run.';
    }
  }


  private async restoreRun() {

    if (!this.threadId) {
      return;
    }


    try {

      const state =
        await this.agentService
          .getRun(
            this.threadId
          );


      this.status =
        state.status;


      this.answer =
        state.finalAnswer || '';


      this.pendingApproval =
        state.pendingApproval;


      if (
        state.status ===
        'completed'
      ) {

        localStorage.removeItem(
          'activeAgentThreadId'
        );
      }

    } catch {

      localStorage.removeItem(
        'activeAgentThreadId'
      );

      this.threadId =
        null;
    }
  }
}