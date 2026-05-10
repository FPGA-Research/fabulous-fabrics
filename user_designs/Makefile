export PDK 		?= ihp-sg13g2
export FABRIC 		?= classic_fabric_10x10
export TILE_LIBRARY 	?= classic

$(info $(PDK))
$(info $(FABRIC))
$(info $(TILE_LIBRARY))

# Get the design names
DESIGNS :=  $(patsubst designs/${TILE_LIBRARY}/%/,%,$(wildcard designs/${TILE_LIBRARY}/*/)) 

ifneq ($(FABRIC),classic_fabric_heichips25)
DESIGNS := $(filter-out ihp_sram_1024x32_1rw,$(DESIGNS))
DESIGNS := $(filter-out mem_1024x32_1rw,$(DESIGNS))
endif

ifeq ($(FABRIC),classic_fabric_heichips25)
DESIGNS := $(filter-out macc_8x8_20,$(DESIGNS))
DESIGNS := $(filter-out ram_32x4_2r_1w,$(DESIGNS))
DESIGNS := $(filter-out register_file,$(DESIGNS))
endif

DESIGNS_CLEAN := $(addsuffix -clean,$(DESIGNS))
DESIGNS_SYNTH := $(addsuffix -synth,$(DESIGNS))
DESIGNS_PNR := $(addsuffix -pnr,$(DESIGNS))
DESIGNS_BIT := $(addsuffix -bit,$(DESIGNS))
DESIGNS_HEX := $(addsuffix -hex,$(DESIGNS))

all: $(DESIGNS)
.PHONY: all

clean: $(DESIGNS_CLEAN)
.PHONY: clean

$(DESIGNS):
	cd designs/${TILE_LIBRARY}/$@; make
.PHONY: $(DESIGNS)

$(DESIGNS_CLEAN):
	cd designs/${TILE_LIBRARY}/$(subst -clean,,$@); make clean
.PHONY: $(DESIGNS_CLEAN)

$(DESIGNS_SYNTH):
	cd designs/${TILE_LIBRARY}/$(subst -synth,,$@); make synth
.PHONY: $(DESIGNS_SYNTH)

$(DESIGNS_PNR):
	cd designs/${TILE_LIBRARY}/$(subst -synth,,$@); make pnr
.PHONY: $(DESIGNS_PNR)

$(DESIGNS_BIT):
	cd designs/${TILE_LIBRARY}/$(subst -synth,,$@); make bitstream
.PHONY: $(DESIGNS_BIT)

$(DESIGNS_HEX):
	cd designs/${TILE_LIBRARY}/$(subst -synth,,$@); make hex
.PHONY: $(DESIGNS_HEX)
