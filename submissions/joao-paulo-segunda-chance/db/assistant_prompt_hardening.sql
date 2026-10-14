-- Identifies executions started after the prompt-injection hardening.
-- Existing executions keep their original prompt_version.
alter table assistant.executions alter column prompt_version set default '1.1.0';
