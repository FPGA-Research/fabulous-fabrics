// SPDX-FileCopyrightText: © 2026 FABulous Contributors
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module register_file (
    input  wire       clk1,
    input  wire       clk2,
    input  wire       rst,
    input  wire       ena,
    
    input  wire [4:0] addr_a,
    input  wire [4:0] addr_b,
    input  wire [1:0] addr_c,
    
    // Input word
    input  wire [3:0] word_a,
    
    // Output words
    output wire [3:0] word_b,
    output wire [3:0] word_c
);

    logic clk1_buf;

    GBUF clock1_buf (
      .IN   (clk1),
      .OUT  (clk1_buf)
    );

    logic clk2_buf;

    GBUF clock2_buf (
      .IN   (clk2),
      .OUT  (clk2_buf)
    );

    logic [3:0] mem [32];

    // Port A
    always_ff @(posedge clk1_buf) begin
        mem[addr_a] <= word_a;
    end

    logic [3:0] word_b_reg;

    // Port B
    always_ff @(posedge clk2_buf) begin
        word_b_reg <= mem[addr_b]; 
    end
    
    assign word_b = word_b_reg;
    
    // Port C
    assign word_c = mem[{3'b0, addr_c}];

endmodule
