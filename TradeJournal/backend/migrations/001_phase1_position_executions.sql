-- Apply once to the intradaytrading MySQL database used by TradeJournal.
ALTER TABLE trade_log
  ADD COLUMN is_phase1_position TINYINT NOT NULL DEFAULT 0,
  ADD COLUMN open_quantity BIGINT NULL,
  ADD COLUMN total_entered_quantity BIGINT NULL,
  ADD COLUMN remaining_avg_entry_price DECIMAL(18,6) NULL,
  ADD COLUMN realized_gross_pnl DECIMAL(24,6) NULL,
  ADD COLUMN total_entry_notional DECIMAL(24,6) NULL,
  ADD COLUMN realized_gross_pnl_pct DECIMAL(9,4) NULL;

CREATE TABLE trade_execution (
  id BIGINT NOT NULL AUTO_INCREMENT,
  trade_id BIGINT NOT NULL,
  sequence INT NOT NULL,
  event_type ENUM('ENTRY','ADD','EXIT') NOT NULL,
  side ENUM('BUY','SELL') NOT NULL,
  quantity BIGINT NOT NULL,
  price DECIMAL(18,6) NOT NULL,
  execution_timestamp DATETIME NOT NULL,
  reason VARCHAR(128) NULL,
  note TEXT NULL,
  client_request_id VARCHAR(64) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_trade_execution_trade FOREIGN KEY (trade_id) REFERENCES trade_log(id),
  CONSTRAINT uq_trade_execution_sequence UNIQUE (trade_id, sequence),
  CONSTRAINT uq_trade_execution_request UNIQUE (trade_id, client_request_id),
  KEY idx_trade_execution_time (trade_id, execution_timestamp, sequence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
