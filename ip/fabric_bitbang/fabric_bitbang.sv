// SPDX-FileCopyrightText: © 2026 FABulous Contributors
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

/*
Sample data from data_i whenever there's
a rising edge on sample_i. Once 32 bits
have been acquired, output the frame.
*/

module fabric_bitbang #(
    parameter FRAME_BITS_PER_ROW = 32
)(
    input  logic  clk_i,
    input  logic  rst_ni,
    
    input  logic  sample_i,
    input  logic  data_i,

    // Bitstream data
    output logic [FRAME_BITS_PER_ROW-1:0] bitstream_data_o,
    output logic        bitstream_valid_o
);
    logic [$clog2(FRAME_BITS_PER_ROW)-1:0] bit_counter;
    logic [FRAME_BITS_PER_ROW-1:0] bitstream_data;
    
    logic sample_d;
    logic do_sample;
    
    always_ff @(posedge clk_i) begin
        sample_d <= sample_i;
    end
    
    // Always sample a signal upon rising
    // edge on sample_i
    assign do_sample = !sample_d && sample_i;
    
    always_ff @(posedge clk_i) begin
        if (!rst_ni) begin
            bit_counter <= '0;
            bitstream_data <= '0;
            bitstream_valid_o <= '0;
        end else begin
            bitstream_valid_o <= '0;
            if (do_sample) begin
                bit_counter <= bit_counter + 1;
                bitstream_data <= {bitstream_data[FRAME_BITS_PER_ROW-2:0], data_i};
                bitstream_valid_o <= bit_counter == FRAME_BITS_PER_ROW-1;
            end
        end
    end
    
    assign bitstream_data_o = bitstream_data;

endmodule
