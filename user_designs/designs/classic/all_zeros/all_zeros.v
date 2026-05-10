// SPDX-FileCopyrightText: © 2026 FABulous Contributors
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module all_zeros (
    `ifdef CLASSIC_FABRIC_HEICHIPS25
    output wire [31:0] all
    `else
    output wire [27:0] all
    `endif
);

    assign all = '0;

endmodule
